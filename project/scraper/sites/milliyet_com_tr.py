
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from dateutil import parser
import pytz
import json 
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.milliyet.com.tr/")
def get_news_links_milliyet(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.milliyet.com.tr/son-dakika-haberleri/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        base_website_url = "https://www.milliyet.com.tr"
        timeline_links = soup.find('div', class_='timeline__links')
        
        if timeline_links:
            timeline_links_f = timeline_links.find_all('div','timeline__link')
            for timeline_link in timeline_links_f:
                a_class = timeline_link.find('a')
                if a_class and a_class.has_attr('href'):
                    link = a_class['href']
                    links.append(base_website_url+link)

        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_milliyet(link)

            process_article_data(
            source_link="https://www.milliyet.com.tr/",
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
    
    
def fetch_article_details_milliyet(url):
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
        
        
        #content images
        
        
        
        image_divs = soup.find_all('div', class_='news-fullwith-block')
        
        if image_divs:
            for image_div in image_divs:
                image_tag = image_div.find('img')
                if image_tag and image_tag.get('src'):
                    image_url = image_tag['src']
                    gallery_images.append(image_url)
                              
        
        #content almaq
        
        script_tag = soup.find("script", {"type": "application/ld+json"})
        article_body = ""

        if script_tag:
            try:
                json_data = json.loads(script_tag.string)
                article_body = json_data.get("articleBody", "")
            except json.JSONDecodeError:
                article_body = ""

        
        formatted_article_body_text = article_body.replace("\n", "</p><p>")

        formatted_article_body = f"<p>{formatted_article_body_text}</p>"

        content = formatted_article_body
        
        #image almaq
        
        image = soup.find('div', class_='news-media').find('img')
        image_url = image['data-src'] if image else None

        #date almaq
        meta_tag = soup.find("meta", {"name":"datePublished"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None
            

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
