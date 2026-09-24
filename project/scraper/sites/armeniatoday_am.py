import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags, extract_gallery_images
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://armeniatoday.am/")
def get_news_links_armeniatoday(request):
    sitemap_url = Source.objects.get(link="https://armeniatoday.am/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        links = []
        link_set = set()
        
        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_description = item.find("description").text.strip() if item.find("description") else None
            rss_content = item.find("content:encoded").text.strip() if item.find("content:encoded") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None

            if link and rss_description and rss_content and rss_title and rss_date:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, rss_description, rss_content, rss_title, rss_date))
                    link_set.add(link)
        
        for link, rss_description, rss_content, rss_title, rss_date in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_armeniatoday(link)
            
            if not description:
                description = rss_description
            if not content:
                content = rss_content
            if not title:
                title = rss_title
            if not news_shared_date:
                news_shared_date = rss_date

            process_article_data(
                source_link="https://armeniatoday.am/",
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

    
def fetch_article_details_armeniatoday(url):
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
        if soup.find("div", class_="jeg_video_container"):
            return None, None, None, None, None, None
        
        title = scrape_meta_title(soup)
        if "прямое включение" in title:
            return None, None, None, None, None, None
        description = scrape_meta_description(soup)
            
        content_element = soup.find('div', class_='entry-content no-share')
        if content_element:
            news_content = content_element.find('div', class_='content-inner')
            if news_content:
                
                for div_tg_class in news_content.find_all('div', class_='telegram-banner'):
                    div_tg_class.decompose()
                    
                for div_tag_class in news_content.find_all('div', class_='jeg_post_tags'):
                    div_tag_class.decompose()
                    
                for ins_class in news_content.find_all('ins', class_='adsbygoogle'):
                    ins_class.decompose()

                gallery_images = extract_gallery_images(news_content)
                clean_soup_tags(soup, news_content)
                content = clean_donya_e_eqtesad_com(news_content.prettify())
                content = clean_html_withregex(content)
                    
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
    