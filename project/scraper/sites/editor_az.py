import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from dateutil import parser
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://editor.az/")
def get_news_links_editor(request):
    sitemap_url = Source.objects.get(link="https://editor.az/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link :
                if link not in link_set:
                    
                    links.append((link))
                    link_set.add(link)
        
        
        for link in links[:10]:
            
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_editor(link)
            
            process_article_data(
            source_link="https://editor.az/",
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
    
    
    
def fetch_article_details_editor(url):
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

        main_div = soup.find('div', class_='main-entry')
        if main_div:
            single_div = soup.find('div', class_='single-content')
            if single_div:
                
                content_element = soup.find('div', class_='entry-content')
                if content_element:
                    
                    for style in content_element.find_all('style'):
                        style.decompose()
                        
                    for div_class in content_element.find_all('div', class_=['social-follow','entry-share']):
                        div_class.decompose()

                    gallery_images = extract_gallery_images(content_element)
                    clean_soup_tags(soup, content_element)
                    content = clean_donya_e_eqtesad_com(content_element.prettify())
                    content = clean_html_withregex(content)

                else:
                    content = None
            else:
                content = None
                
        else:
            content = None
        
        
        image_url = scrape_meta_url(soup)
            
            
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
    
