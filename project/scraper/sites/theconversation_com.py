# rss: https://theconversation.com/global/home-page.atom
# region: Australia
import requests
from bs4 import BeautifulSoup
from scraper.models import Source
import re
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://theconversation.com/global")
def get_news_links_theconversation_com(request=None):
    sitemap_url = Source.objects.get(link="https://theconversation.com/global").rss_link
    headers  = {"User-Agent":"Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('entry')
        
        links = []
        link_set = set()
        
        for item in items:
            link_tag = item.find("link", rel="alternate")
            link = link_tag.get("href") if link_tag else None

            if link and link not in link_set:
                links.append(link)
                link_set.add(link)
                
        for link in links[:25]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_theconversation_com(link)
            
            process_article_data(
                source_link="https://theconversation.com/global",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        None
    

def fetch_article_details_theconversation_com(url):
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
        news_shared_date = scrape_meta_news_shared_date(soup)
        image_url = scrape_meta_url(soup)
        
        #content    

        article_text_div = soup.find("div", class_="content-body")

        if article_text_div:      
            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for invite_div in article_text_div.find_all("div", class_="inline-invite"):
                invite_div.decompose()

            for tag in article_text_div.find_all("div", class_="promo"):
                tag.decompose()

            for tag in article_text_div.find_all("div", class_="audio-player"):
                tag.decompose()

            for tag in article_text_div.find_all("div", class_="ytp-cued-thumbnail-overlay"):
                tag.decompose()

            for fc in article_text_div.find_all("figure"):
                fc.decompose()

            pattern = re.compile(r"^(READ MORE:|WATCH:)", re.I)
            for strong_tag in soup.find_all("strong"):
                if pattern.match(strong_tag.get_text(strip=True)):
                    strong_tag.find_parent("p").decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    
