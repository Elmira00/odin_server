import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from dateutil import parser
import pytz
import re
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.mashreghnews.ir/")
def get_news_links_mashreghnews_ir(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://www.mashreghnews.ir/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        
        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_mashreghnews_ir(link)
            
            
                
            process_article_data(
            source_link="https://www.mashreghnews.ir/",
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

        
        
        
def fetch_article_details_mashreghnews_ir(url):
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
        
        div_class = soup.find('div', class_='item-body')
        if div_class:
            article_text_div = div_class.find('div', class_='item-text')
            if article_text_div:
                        
                            
                gallery_images = extract_gallery_images(article_text_div)


                clean_soup_tags(soup, article_text_div)
                content = clean_donya_e_eqtesad_com(article_text_div.prettify())
                content = clean_html_withregex(content)
        else:
            content = None

        image_url = scrape_meta_url(soup)

        meta_tag_time = soup.find("meta", {"property": "article:published_time"})
        
        if meta_tag_time:
            date_str = meta_tag_time["content"] 
            dt_utc = parser.parse(date_str)  
            baku_tz = pytz.timezone("Asia/Baku")
            news_shared_date = dt_utc.astimezone(baku_tz)
        else:
            news_shared_date = None


        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
