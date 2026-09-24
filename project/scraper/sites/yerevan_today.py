import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
import re



from utils.decorators import check_source_active


@check_source_active("https://yerevan.today/")
def get_news_links_yerevan_today(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://yerevan.today/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []        
        
        ajax_paginator = soup.find('div', class_='et_pb_ajax_pagination_container')
        if ajax_paginator:
            infinite_class = ajax_paginator.find_all('h2', class_='entry-title')    
            if infinite_class:
                for infinite in infinite_class:
                    a_class = infinite.find('a')
                    if a_class and a_class.has_attr('href'):
                        link = a_class['href']
                        links.append(link)
                            

        for link in links[:12]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_yerevan_today(link)

            process_article_data(
            source_link="https://yerevan.today/",
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
    

    
def fetch_article_details_yerevan_today(url):
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

    
        article_div_class = soup.find('div', class_='et_pb_module et_pb_post_content et_pb_post_content_0_tb_body post-content-size')
        if article_div_class:
                
            gallery_images = extract_gallery_images(article_div_class)   
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)   
        else:
            content = None

        
        
        image_wrapper_div = soup.find('div', class_='et_pb_title_featured_container')
        if image_wrapper_div:
            image_element = soup.find('span', class_='et_pb_image_wrap')
            if image_element:
                image = image_element.find('img')
                image_url = image['src'] if image else None
        else:
            
            meta_tag_image = soup.find("meta", {"property": "og:image"})
            image_url = meta_tag_image["content"] if meta_tag_image and "content" in meta_tag_image.attrs else None


        meta_tag_time = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_time:
            date_str = meta_tag_time["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None
            
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
