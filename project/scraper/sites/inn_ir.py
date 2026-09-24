# region: iran
import requests
from bs4 import BeautifulSoup

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from datetime import datetime
from dateutil import parser


def get_news_links_inn_ir(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://inn.ir/news/service/international"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://inn.ir/news"

    news_cards = soup.find_all('article', class_='item-content news-mode')    

    for news_card in news_cards:
        link = news_card.find('a')['href']
        if link and link not in link_set:
            links.append(link)
            link_set.add(link)

    for link in links[:28]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_inn_ir(link)
        process_article_data(
            source_link="https://inn.ir/news",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date
        )
        
    else:
        return None


def fetch_article_details_inn_ir(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        tag = soup.find("meta", {'property': 'article:published_time'})

        if tag:
            news_shared_date = tag['content']
        else:
            news_shared_date = None

        #content

        article_text_div = soup.find("div", {"class": "content"})

        if article_text_div: 

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ["ImgReport_BG"],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe', 'script', 'svg']):
                tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None