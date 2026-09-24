import requests
from bs4 import BeautifulSoup
import pytz
from dateutil import parser
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://ensafnews.com/")
def get_news_links_esnafnews_com(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://ensafnews.com/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
                
        div_class = soup.find("div", class_="widget-posts-list-container timeline-widget")
        if div_class:
        
            ul_class =  div_class.find("ul", class_="posts-list-items widget-posts-wrapper")
            if ul_class:
                li_classes = ul_class.find_all("li", class_="widget-single-post-item")
                if li_classes:
                    for li in li_classes:
                        a_tag = li.find("a")
                        if a_tag and a_tag.has_attr("href"):
                            link = a_tag["href"]
                            links.append(link)
                             

        for link in links[:25]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_esnafnews_com(link)
            
            process_article_data(
            source_link="https://ensafnews.com/",
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
    
    
    
def fetch_article_details_esnafnews_com(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
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

        article_text_div = soup.find('div', class_='entry-content entry clearfix')
        if article_text_div:

            
                    
            unwanted_div_classes = ["post-bottom-meta post-bottom-tags post-tags-modern", "stream-item stream-item-below-post-content",
                                    "stream-item stream-item-in-post stream-item-inline-post aligncenter"]
            
            for div_class in unwanted_div_classes:
                for div in article_text_div.find_all('div', class_=div_class):
                    div.decompose()
                    
                        
            for style in article_text_div.find_all('style'):
                        style.decompose()
                    
            gallery_images = extract_gallery_images(article_text_div)
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None


        image_url = scrape_meta_url(soup)


        meta_tag = soup.find("meta", {"property": "article:published_time"})
        if meta_tag and meta_tag.has_attr("content"):
            date_str = meta_tag["content"] 
            dt = parser.parse(date_str)    
            baku_tz = pytz.timezone("Asia/Baku")
            news_shared_date = dt.astimezone(baku_tz)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
