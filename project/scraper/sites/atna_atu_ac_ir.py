
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
import re
import pytz
from dateutil import parser
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://atna.atu.ac.ir/")
def get_news_links_atna_atu_ac_ir(request):
    
    sitemap_url = Source.objects.get(link="https://atna.atu.ac.ir/").rss_link
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
        
                    dt = parser.parse(pub_date_raw)
                    dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    links.append((link, dt_baku))
                    link_set.add(link)
                
                

        for link, news_shared_date in links[:15]:
            title,description, content, image_url,gallery_images = fetch_article_details_atna_atu_ac_ir(link)
            
            
            process_article_data(
            source_link="https://atna.atu.ac.ir/",
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

        
        
def fetch_article_details_atna_atu_ac_ir(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    
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
        
        
        
        article_text_div = soup.find('div', class_='body')
        if article_text_div:
            
            for script_tag in article_text_div.find_all('style'):
                    script_tag.decompose()


            for image in article_text_div.find_all('img'):
                if image and image.has_attr('src'):
                    src = image['src']
                    if src.startswith('/files'):
                        full_src = 'https://atna.atu.ac.ir' + src
                    else:
                        full_src = src

                    new_img_tag = soup.new_tag('img', src=full_src)
                    image.replace_with(new_img_tag)
                else:
                    image.decompose()

                    
                    
            for a_tag in article_text_div.find_all('a'):
                if a_tag and a_tag.has_attr('href'):
                    href = a_tag['href']
                    if href.startswith('/files'):
                        full_href = 'https://atna.atu.ac.ir' + href
                    else:
                        full_href = href

                    new_a_tag = soup.new_tag('a', href=full_href)
                    new_a_tag.string = a_tag.get_text(strip=True)
                    a_tag.replace_with(new_a_tag)
                else:
                    a_tag.decompose()
                    
                    

            gallery_images = extract_gallery_images(article_text_div)

            
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
            
                
        else:
            content = None


        image_url = scrape_meta_url(soup)


        return title, description, content, image_url,gallery_images
    
    else:
        return None, None, None, None,None
