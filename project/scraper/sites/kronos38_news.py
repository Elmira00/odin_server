# https://kronos41.news/feed/
import requests
from bs4 import BeautifulSoup
from scraper.models import Source
from dateutil import parser
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://kronos38.news/")
def get_news_links_kronos38(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://kronos38.news/").rss_link
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("media:thumbnail")["url"] if item.find("media:thumbnail") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_description = item.find("description").text.strip() if item.find("description") else None
            if link and rss_image and rss_title and rss_description:
                if link not in link_set:
                    links.append((link, rss_image, rss_title, rss_description))
                    link_set.add(link)

        for link, rss_image, rss_title, rss_description in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_kronos38(link)
            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            
            process_article_data(
                source_link="https://kronos38.news/",
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
    
    
def fetch_article_details_kronos38(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers, timeout=10)
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
        
        div_class = soup.find('div', class_='entry-content rbct clearfix is-highlight-shares')
        if div_class:

            for div_class_add in div_class.find_all('div', class_='ad-wrap ad-script-wrap'):
                div_class_add.decompose()   
                
            gallery_images = extract_gallery_images(div_class)
            clean_soup_tags(soup, div_class)
            content = clean_donya_e_eqtesad_com(div_class.prettify())
            content = clean_html_withregex(content)
           
        else:
            content = None
            
        #image almaq
        
        image_url = scrape_meta_url(soup)
            
        # news_shared Alma
        meta_tag_news_shared = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_news_shared:
            date_str = meta_tag_news_shared.get('content', '')
            try:

                date_str = date_str.replace(' (UTC ', 'Z') 
                news_shared_date = parser.isoparse(date_str)
            except ValueError:
                news_shared_date = None
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
