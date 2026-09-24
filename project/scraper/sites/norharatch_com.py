import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
import re




from utils.decorators import check_source_active


@check_source_active("https://norharatch.com/")
def get_news_links_norharatch_com(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://norharatch.com/news-hy/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []                     
            
        a_tags = soup.find_all('a', class_='elementor-post__thumbnail__link')               
        if a_tags:
            for a_tag in a_tags:
                if a_tag and a_tag.has_attr('href'):
                    link = a_tag['href']                
                    links.append(link)
                        

        for link in links[:12]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_norharatch_com(link)

            process_article_data(
            source_link="https://norharatch.com/",
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
    

    
def fetch_article_details_norharatch_com(url):
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
        description = None
            
        # Content
        div_class = soup.find('div', class_='elementor-widget-text-editor')
        if div_class:
            
            gallery_images = extract_gallery_images(div_class)
            clean_soup_tags(soup, div_class)
            content = clean_donya_e_eqtesad_com(div_class.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
            
            
        image_url = scrape_meta_url(soup)
        
        
        # Time
        
        meta_tag = soup.find("meta", {"property": "article:modified_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)
            news_shared_date = dt.astimezone(pytz.UTC)

        else:
            date_item = soup.find('li', {'class': 'elementor-icon-list-item', 'itemprop': 'datePublished'})
            if date_item:
                time_element = date_item.find('time')
                if time_element:
                    date_text = time_element.get_text().strip()

                    try:
                        day, month, year = map(int, date_text.split("/"))

                        fixed_dt = datetime(year, month, day, 1, 0)

                        news_shared_date = pytz.UTC.localize(fixed_dt)

                    except ValueError as e:
                        news_shared_date = None
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
                
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
