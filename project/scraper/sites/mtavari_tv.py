import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re
import pytz
from dateutil import parser
from datetime import datetime



from utils.decorators import check_source_active


@check_source_active("https://mtavari.tv/")
def get_news_links_mtavari_tv(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://mtavari.tv/news/archive"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []              
        
        base_website_url = "https://mtavari.tv"  
    
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/news/'):
                links.append(base_website_url + href) 
                        

        for link in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_mtavari_tv(link)

            process_article_data(
            source_link="https://mtavari.tv/",
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
    

    
def fetch_article_details_mtavari_tv(url):
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
        
        
        
        div_class = soup.find('div', class_='EditorContent__EditorContentWrapper-ygblm0-0 dzgBwY')
        
        if div_class:
                
            gallery_images = extract_gallery_images(div_class)
            clean_soup_tags(soup, div_class)
            content = clean_donya_e_eqtesad_com(div_class.prettify())
            content = clean_html_withregex(content)
                
                
        else:
            content = None

        
        image_url = scrape_meta_url(soup)

            
            
        inner_div = soup.find('div', class_='id__Published-bhuaj0-18 kqeamR')

        if inner_div:
            
                
            time_tag = inner_div.find('time')

            if time_tag and time_tag.has_attr('datetime'):
                datetime_str = time_tag['datetime']
                    
                dt = datetime.fromisoformat(datetime_str[:-6])  
                formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                news_shared_date = formatted_datetime
            else:
                    news_shared_date = None
                    
        else:
            news_shared_date = None
                
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
