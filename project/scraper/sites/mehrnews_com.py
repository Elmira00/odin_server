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


@check_source_active("https://www.mehrnews.com/")
def get_news_links_mehrnews_com(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.mehrnews.com/archive"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        website_base_url = "https://www.mehrnews.com"
        
        
        li_classes = soup.find_all('li')    
        
        if li_classes:
            for li_class in li_classes:
                figure_tag = li_class.find('figure')
                if figure_tag:
                    a_class = figure_tag.find('a')
                    if a_class and a_class.has_attr('href'):
                        link = a_class['href']
                        links.append(website_base_url + link)
                        
                        
        

        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_mehrnews_com(link)

            process_article_data(
            source_link="https://www.mehrnews.com/",
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
    

    
def fetch_article_details_mehrnews_com(url):
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

        article_text_div = soup.find('div', class_='item-text')
        if article_text_div:

        
            gallery_images = extract_gallery_images(article_text_div)


            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None



        image_url = scrape_meta_url(soup)

        # Tarix

        meta_tag = soup.find("meta", {"property": "article:published_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
