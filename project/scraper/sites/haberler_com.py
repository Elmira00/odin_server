import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser



from utils.decorators import check_source_active


@check_source_active("https://www.haberler.com/")
def get_news_links_haberler(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.haberler.com/son-dakika/"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        news_container_div = soup.find('div', class_='new3sondk-news-container')
        website_base_url = "https://www.haberler.com"
        
        if news_container_div:
            news_cards = news_container_div.find_all('div', class_='new3sondk-news-card')
            
            if news_cards:
                for news_card in news_cards:
                    news_card_body = news_card.find('div', class_='new3sondk-card-body')
                    if news_card_body:
                        a_class = news_card_body.find('a', class_='new3sondk-news')
                        if a_class and a_class.has_attr('href'):
                            link = a_class['href']
                            links.append(website_base_url + link)

        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_haberler(link)

            process_article_data(
            source_link="https://www.haberler.com/",
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
    

    
def fetch_article_details_haberler(url):
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
        
        
        
        main_class = soup.find('div', id='news')
        if main_class:

            #gallery_images = extract_gallery_images(main_class)

            newstags = soup.find('div', id='nwsKeywords')
            if newstags:
                newstags.decompose()
                
            editorsade = soup.find('div', class_='editorSade')
            if editorsade:
                editorsade.decompose()
                
            clean_soup_tags(soup, main_class)
            content = clean_donya_e_eqtesad_com(main_class.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
        
        
        
        tag = soup.find("meta", {"property": "og:image"})
        if tag and "content" in tag.attrs:
            temp_image_url = tag["content"]
            if "/mstatic/haberlercom_haberi.jpg" in temp_image_url:
                image_url = None
            else:
                image_url = temp_image_url
        else:
            image_url = None                    
            
                    
            
            
        meta_tag = soup.find("meta", {"name": "datePublished"})
        if meta_tag:
            date_str = meta_tag["content"]  

            dt = parser.parse(date_str)

            news_shared_date = dt.astimezone(pytz.UTC) 
        else:
            news_shared_date = None

        image_url = scrape_meta_url(soup) if not image_url else image_url
            

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
