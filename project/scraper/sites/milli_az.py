import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from dateutil import parser
import pytz

from utils.decorators import check_source_active


@check_source_active("https://news.milli.az/")
def get_news_links_milli(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://news.milli.az/").rss_link
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None
            if link and rss_image and link not in link_set:
                links.append((link, rss_image))
                link_set.add(link)
        
        for link, rss_image in links[:25]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_milli(link)
            if not image_url:
                image_url = rss_image
            
            process_article_data(
                source_link="https://news.milli.az/",
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
    

def fetch_article_details_milli(url):
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
            
        div_class = soup.find('div', class_='article_text')
        if div_class:
            clean_soup_tags(soup, div_class)
            content = clean_donya_e_eqtesad_com(div_class.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
            
        div_class = soup.find('div', class_='article-gallery')
        if div_class:
            ul_class = div_class.find('ul', class_='images-list')
            if ul_class:
                li_classes = ul_class.find_all('li')
                for li_class in li_classes:
                    img_class = li_class.find('img')
                    if img_class and img_class.get('src'):
                        gallery_images.append(img_class['src'])  
                        
        #IMAGE ALMAQ
        
        image_url = scrape_meta_url(soup)

        # body'de 
        if not image_url:
            img_tag = soup.find('img', class_='content-img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']

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
    