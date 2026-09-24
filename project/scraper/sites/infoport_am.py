import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
import re
from datetime import datetime


from utils.decorators import check_source_active


@check_source_active("https://infoport.am/")
def get_news_links_infoport_am(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://infoport.am/news"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        
        base_website_url = "https://infoport.am"
        
        all_post = soup.find_all('div', class_='posts-content')
        for post in all_post:
            a_tag = post.find('a')
            if a_tag and a_tag.has_attr('href'):
                link = a_tag['href']
                links.append((base_website_url+link))
                            

        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_infoport_am(link)

            process_article_data(
            source_link="https://infoport.am/",
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
    

    
def fetch_article_details_infoport_am(url):
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
        
        description = None
    
        article_div_class = soup.find('div', class_='article-content')
        if article_div_class:


            gallery_images = extract_gallery_images(article_div_class)

            unwanted_ul_classes = ['entry-meta', 'category']
            for ul_class in unwanted_ul_classes:
                ul_elements = article_div_class.find_all('ul', class_=ul_class)
                for ul in ul_elements:
                    ul.decompose()
                    
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
                        
        else:
            content = None

        
        
        meta_tag_image = soup.find("meta", {"property": "og:image"})
        imagee_url = meta_tag_image["content"] if meta_tag_image and "content" in meta_tag_image.attrs else None
        if imagee_url:
            image_url = "https://infoport.am" + imagee_url
        else:
            image_url = None


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
