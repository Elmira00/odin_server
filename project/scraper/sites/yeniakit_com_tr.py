import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
from datetime import timedelta
import re

from utils.decorators import check_source_active


@check_source_active("https://www.yeniakit.com.tr/")
def get_news_links_yeniakit(request):
    sitemap_url = "https://www.yeniakit.com.tr/haber"
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        section_class = soup.find('section', class_='functional-horizontal-module')
        if section_class:
            div_elements = soup.find_all('div', class_='element')
            if div_elements:
                for div_element in div_elements:
                    a_tag = div_element.find('a')
                    if a_tag and a_tag.has_attr('href'):
                        link = a_tag['href']
                        links.append(link)
                                        
        for link in links[:50]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_yeniakit(link)
            
            process_article_data(
                source_link="https://www.yeniakit.com.tr/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        return None
    

def fetch_article_details_yeniakit(url):
    response = requests.get(url)
    if response.url != url:
        return None, None, None, None, None, None
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

        # Content Alma
        news_content_div = soup.find('div', class_='default-news-content')
        if news_content_div:
            div_for_reclam = news_content_div.find('div', class_='content forReklamUp')
            if div_for_reclam:
                
                for reclam_div in news_content_div.find_all('div',class_="similarNews"):
                    if reclam_div:
                        reclam_div.decompose()
                
                gallery_images = extract_gallery_images(div_for_reclam)
                gallery_images = [img for img in gallery_images if not img.endswith(".gif")]   
                clean_soup_tags(soup, div_for_reclam)
                content = clean_donya_e_eqtesad_com(div_for_reclam.prettify())
                content = clean_html_withregex(content)      
        else:
            content = None

        image_url = scrape_meta_url(soup)
        #updated img scraping 
        if not image_url:
            figure_tag = soup.find('figure', class_='image')
            
            if figure_tag:
                img_tag = figure_tag.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag['src']
            if not image_url:
                article_tag = soup.find('article')
                if article_tag:
                    img_tag = article_tag.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag['src']
        # Tarih Alma
        meta_tag = soup.find("meta", {"name": "datePublished"})
        if meta_tag:
            date_str = meta_tag["content"]
            news_shared_date = parser.parse(date_str)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
