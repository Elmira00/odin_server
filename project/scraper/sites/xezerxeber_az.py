
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime,timedelta
from dateutil import parser
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz


from utils.decorators import check_source_active


@check_source_active("https://www.xezerxeber.az/")
def get_news_links_xezerxeber(request):
    sitemap_url = Source.objects.get(link="https://www.xezerxeber.az/").rss_link
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')

        items = soup.find_all('entry')
 
        links = [item.find('link', rel='alternate')['href'] for item in items if item.find('link', rel='alternate')]

        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_xezerxeber(link)

            process_article_data(
            source_link="https://www.xezerxeber.az/",
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

        
        
        
        
def fetch_article_details_xezerxeber(url):
    response = requests.get(url)
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


        content_main = soup.find('div', class_='box shadow mb-7 p-3 md:p-5 bg-white')
        if content_main:
            news_content = content_main.find('div', class_='content-text leading-relaxed')
            if news_content:
                gallery_images = extract_gallery_images(news_content)
                clean_soup_tags(soup, news_content)
                content = clean_donya_e_eqtesad_com(news_content.prettify())
                content = clean_html_withregex(content)
            else:
                content = None
        else:
            content = None


        image_url = scrape_meta_url(soup)
            
              
        meta_tag = soup.find("meta", {"property":"og:published_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
