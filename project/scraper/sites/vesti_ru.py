# region: Rusiya

import requests
from bs4 import BeautifulSoup

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from datetime import datetime


def get_news_links_vesti_ru(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.vesti.ru/news"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://www.vesti.ru"

    news_cards = soup.find_all('a', class_='list__pic-wrapper')    

    for news_card in news_cards:
        link = news_card['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:20]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_vesti_ru(link)
        process_article_data(
            source_link="https://www.vesti.ru/",
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


def fetch_article_details_vesti_ru(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86 _64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
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

        article = soup.find("article", class_="article")
        news_shared_date = (
            timezone.make_aware(
                datetime.strptime(article["data-datepub"], "%Y-%m-%d %H:%M:%S"),
                timezone.get_current_timezone()
            )
            if article and article.has_attr("data-datepub")
            else None
        )

        #content

        article_text_div = soup.find("div", {"class": "article__text"})

        if article_text_div: 

            article_text_div.find('img').decompose()

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ["subheader",],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe', 'script']):
                tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None