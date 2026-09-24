import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
import pytz
from dateutil import parser
import re



from utils.decorators import check_source_active


@check_source_active("https://uz.sputniknews.ru/")
def get_news_links_uz_sputniknews_ru(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://uz.sputniknews.ru/news/"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        website_base_url = "https://uz.sputniknews.ru"
        
        
        news_cards = soup.find_all('div', class_='list__item')    
        
        if news_cards:
            for news_card in news_cards:
                news_card_body = news_card.find('div', class_='list__content')
                if news_card_body:
                    a_class = news_card_body.find('a', class_='list__title')
                    if a_class and a_class.has_attr('href'):
                        link = a_class['href']
                        links.append(website_base_url + link)

        for link in links[:20]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_uz_sputniknews_ru(link)

            process_article_data(
            source_link="https://uz.sputniknews.ru/",
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

    
def fetch_article_details_uz_sputniknews_ru(url):
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


        #content     

        article_text_div = soup.find('div', class_='article__body')
        if article_text_div:


            main_photo_divs = soup.find_all("div", attrs={"class": "article__block", "data-article": "main-photo"})
            for div in main_photo_divs:
                div.decompose()

            cleaned_blocks = []
            for block in article_text_div.find_all("div", class_="article__block", recursive=False):
                inner_content = block.find("div", recursive=False)
                if inner_content:
                    cleaned_blocks.append(inner_content.prettify())  

            first_cleaned_block_html = "\n".join(cleaned_blocks)
            first_cleaned_block_soup = BeautifulSoup(first_cleaned_block_html, 'html.parser')
            
            gallery_images = extract_gallery_images(first_cleaned_block_soup)

            clean_soup_tags(soup, first_cleaned_block_soup)
            content = clean_donya_e_eqtesad_com(first_cleaned_block_soup.prettify())
            content = clean_html_withregex(content)
            
        else:
            content = None



        image_url = scrape_meta_url(soup)

        # Tarix
        meta_tag_date_tag = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_date_tag:
            date_str = meta_tag_date_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
