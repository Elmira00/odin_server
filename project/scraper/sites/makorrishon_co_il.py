# region: Israel
import requests
from bs4 import BeautifulSoup

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from datetime import datetime


def get_news_links_makorrishon_co_il(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.makorrishon.co.il/news"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://www.makorrishon.co.il"

    news_cards = soup.find_all('article', class_='relative flex items-center w-full h-[16rem] overflow-hidden no-underline bg-[#FFFFFF] @container-xl:flex-reverse @container-xs:h-[15.1rem] @container-xl:h-[20.6rem] hover:bg-[#84AFD3] hover:bg-opacity-20')    

    for news_card in news_cards:
        link = news_card.find('a')['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:75]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_makorrishon_co_il(link)
        process_article_data(
            source_link="https://www.makorrishon.co.il",
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


def fetch_article_details_makorrishon_co_il(url):
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

        title = soup.find('meta', {'name': 'og:title'})['content']
        description = soup.find('meta', {'name': 'og:description'})['content']
        image_url = soup.find('meta', {'name': 'og:image'})['content']

        news_shared_date = soup.find('meta', {'name': 'article:published_time'})['content']

        #content

        article_text_div = soup.find("main", {"class": "article-content-area"})

        if article_text_div: 

            CLASS_MATCHES = {
                "div": ['with-spacing_spacing__j_82t'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe', 'script', 'div', 'section']):
                tag.decompose()
            
            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ['https://www.makorrishon.co.il' + img if img.startswith('/') else img for img in gallery_images]

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None