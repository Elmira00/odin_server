
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re
import pytz


from utils.decorators import check_source_active


@check_source_active("https://www.zeitoons.com/")
def get_news_links_zeitoons_com(request):
    
    sitemap_url = "https://www.zeitoons.com/feed"
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set() 
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

            if link and pub_date_raw:
                dt = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                links.append((link, dt_baku))
                link_set.add(link) 
                
                

        for link, news_shared_date in links[:30]:
            title,description, content, image_url,gallery_images = fetch_article_details_zeitoons_com(link)
            
            process_article_data(
            source_link="https://www.zeitoons.com/",
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
            
    
    
def fetch_article_details_zeitoons_com(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = scrape_meta_title(soup)

        description = scrape_meta_description(soup)


        #content     

        article_text_div = soup.find('div', class_='elementor-element elementor-element-58f99d5a elementor-widget elementor-widget-theme-post-content')
        if article_text_div:

        
            gallery_images = extract_gallery_images(article_text_div)
                
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None


        image_url = scrape_meta_url(soup)


        return title, description, content, image_url,gallery_images
    
    else:
        return None, None, None, None,None
