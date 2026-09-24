
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from dateutil import parser
import pytz
import re
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://www.sedayemardom.net/")
def get_news_links_sedayemardom_net(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.sedayemardom.net/?cat=2"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
    
        ul_class = soup.find('ul', id='posts-container')
        if ul_class:
            li_elements = ul_class.find_all('li')
            
            for li in li_elements:
                a_tag = li.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    article_url = a_tag['href']
                    links.append(article_url)

        for link in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_sedayemardom_net(link)

            process_article_data(
            source_link="https://www.sedayemardom.net/",
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
    
    
    
def fetch_article_details_sedayemardom_net(url):
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
        
            
        article_text_div = soup.find('div', class_='pf-content')
        if article_text_div:
            
                    
            unwanted_div_classes = ["printfriendly pf-button pf-button-content pf-alignright"]
            
            for unwanted_div_class in unwanted_div_classes:
                for div in article_text_div.find_all("div", class_=unwanted_div_class):
                    div.decompose()
                    
            for p_tag in article_text_div.find_all('p'):
                if (
                    'به کانال صدای مردم در تلگرام بپیوندید' in p_tag.get_text()
                    or 'telegram.me/sedayemardomdotnet' in p_tag.get_text()
                ):
                    p_tag.decompose()
            gallery_images = extract_gallery_images(article_text_div)
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
        
        image_url = scrape_meta_url(soup)

        #date almaq
        meta_tag_i_tag = soup.find("meta", {"property": "article:published_time"})
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
