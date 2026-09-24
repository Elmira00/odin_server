import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://www.newsgeorgia.ge/")
def get_news_links_newsgeorgia_ge(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.newsgeorgia.ge/newsgeorgia/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []                
        li_tags = soup.find_all('h2', class_='entry-title') 
        for li_tag in li_tags:
            a_tag = li_tag.find('a')
            if a_tag and a_tag.has_attr('href'):
                link = a_tag['href']
                links.append(link) 
                        
        for link in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_newsgeorgia_ge(link)

            process_article_data(
            source_link="https://www.newsgeorgia.ge/",
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
    

def fetch_article_details_newsgeorgia_ge(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers, timeout=10)
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
        if not title:
            title = soup.find("title").text.strip() if soup.find("title") else None
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)        

        #Content
        article_div_class = soup.find('div', class_='entry-content')
        if article_div_class:
            
            unwaned_divs = ['relpost-thumb-wrapper','widget_text awac-wrapper','addtoany_share_save_container addtoany_content addtoany_content_bottom']
                        
            for unwanted_div in unwaned_divs:
                for div in article_div_class.find_all('div', class_=unwanted_div):
                    div.decompose()
                       
            for iframe in article_div_class.find_all('iframe'):
                iframe.decompose()
                
            for blockquote in article_div_class.find_all('blockquote'):
                blockquote.decompose()
                    
            gallery_images = extract_gallery_images(article_div_class)
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
            
                
        else:
            content = None
 
            #Time
        meta_tag = soup.find("meta", {"property":"article:published_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None
                
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
