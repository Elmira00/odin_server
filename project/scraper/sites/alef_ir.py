import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source

from dateutil import parser
import pytz
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://www.alef.ir/")
def get_news_links_alef_ir(request=None):
    sitemap_url = Source.objects.get(link="https://www.alef.ir/").rss_link
    headers  = {"User-Agent":"Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link :
                if link not in link_set:
                    
                    links.append((link))
                    link_set.add(link)
                
                

        for link in links[:40]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_alef_ir(link)
            
            process_article_data(
            source_link="https://www.alef.ir/",
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

        
        
        
def fetch_article_details_alef_ir(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers, timeout=5)
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

        article_text_div = soup.find('div', class_='post-content clearfix mb-3')
        if article_text_div:      
            


            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None


        image_url = scrape_meta_url(soup)
        
        meta_tag_i_tag = soup.find("meta", {"property": "og:article:published_time"})
        if meta_tag_i_tag:
            date_str = meta_tag_i_tag["content"] 
            dt_utc = parser.parse(date_str)  
            baku_tz = pytz.timezone("Asia/Baku")
            news_shared_date = dt_utc.astimezone(baku_tz)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
