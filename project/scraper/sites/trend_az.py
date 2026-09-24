import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
from urllib.parse import urljoin

from utils.decorators import check_source_active


@check_source_active("https://az.trend.az/")
def get_news_links_trend(request):
    sitemap_url = Source.objects.get(link="https://az.trend.az/").rss_link
    response = requests.get(sitemap_url, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        links = []
        link_set = set()
        
        items = soup.find_all('item')
        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and rss_image and rss_title and rss_date:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, rss_image, rss_title, rss_date))
                    link_set.add(link)
        
        for link, rss_image, rss_title, rss_date in links[:20]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_trend(link)
            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not news_shared_date:
                news_shared_date = rss_date
            
            process_article_data(
                source_link="https://az.trend.az/",
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
    
    
def fetch_article_details_trend(url):
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    news_shared_date = None  
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find("div", class_="paid-content-locked"):
            return None, None, None, None, None, None

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
            
        #content images
        article_gallery = soup.find('div', class_='article-gallery')
        
        if article_gallery:
            swiper_wrapper_div = article_gallery.find('div',class_='swiper-wrapper')
            if swiper_wrapper_div:
                
                images = soup.find_all('img',class_="gallery-image")
                if images:
                    for image in images:
                        if image and image.get('src'):
                            image_url = image['src']
                            gallery_images.append(image_url)
        
        content_main = soup.find('div', class_='right-part')
        if content_main:
            news_content = content_main.find('div', class_='article-content article-paddings')
            if news_content:
                gallery_images = extract_gallery_images(news_content)
                clean_soup_tags(soup, news_content)
                content = clean_donya_e_eqtesad_com(news_content.prettify())
                content = clean_html_withregex(content)
            else:
                content = None
        else:
            content = None
            
        image_url_tag = soup.find("meta", {"property": "og:image"})
        if image_url_tag and "content" in image_url_tag.attrs:
            image_url = image_url_tag["content"]
            
            if image_url.startswith("/") or image_url.startswith("/imagen"):
                image_url = urljoin("https://az.trend.az", image_url)
        else:
            image_url = None


        #body'de baxsin
        if not image_url:
            img_div = soup.find('div', class_='image-wrapper')
            if img_div:
                img_tag = img_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag['src']
                    if image_url.startswith("/"):
                        image_url = urljoin("https://az.trend.az", image_url)
            
        # Tarix
        meta_tag_date_tag = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_date_tag:
            date_str = meta_tag_date_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
