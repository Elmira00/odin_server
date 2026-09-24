
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re
import pytz


from utils.decorators import check_source_active


@check_source_active("http://www.irdiplomacy.ir/fa")
def get_news_links_irdiplomacy_ir(request):
    
    sitemap_url = Source.objects.get(link="http://www.irdiplomacy.ir/fa").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

            if link and pub_date_raw:
                if link not in link_set:
                    dt = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                    dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    links.append((link, dt_baku))
                    link_set.add(link)
                
                

        for link, news_shared_date in links[:45]:
            title,description, content, image_url,gallery_images = fetch_article_details_irdiplomacy_ir(link)
            
            process_article_data(
            source_link="http://www.irdiplomacy.ir/fa",
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

    
def fetch_article_details_irdiplomacy_ir(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)

        article_text_div = soup.find('div', class_='content')
        if article_text_div:

            for image_base in article_text_div.find_all('img'):
                if image_base.get('src') and 'news_corner_image' in image_base.get('class', []):
                    image_base.decompose()

            cdn_prefix = "http://www.irdiplomacy.ir"
            images = article_text_div.find_all('img')

            for image in images:
                if image and image.has_attr('src'):
                    src = image['src']
                    
                    if not src.startswith(('http://', 'https://')):
                        full_src = cdn_prefix + src
                    else:
                        full_src = src

                    gallery_images.append(full_src)

            for image in images:
                image.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        # Ana görsel (image_url)
        base_url = "http://www.irdiplomacy.ir"
        image_div = soup.find('div', id='primary-image-container')
        if image_div and image_div.find('img'):
            imagee_url = image_div.find('img')['src']
            if imagee_url:
                image_url = base_url + imagee_url
            else:
                image_url = None
        else:
            image_url = None
        
        return title, description, content, image_url, gallery_images
    
    else:
        return None, None, None, None, None
