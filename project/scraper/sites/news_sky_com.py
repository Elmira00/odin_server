
import requests
from bs4 import BeautifulSoup
from scraper.models import Source
import pytz
from datetime import datetime
import re
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://news.sky.com/")
def get_news_links_skynews_com(request=None):
    sitemap_url = Source.objects.get(link="https://news.sky.com/").rss_link
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
                
        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_skynews_com(link)
            
            process_article_data(
                source_link="https://news.sky.com/",
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
    

def fetch_article_details_skynews_com(url):
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
        image_url = scrape_meta_url(soup)

        date_tag = soup.find('p', class_='sdc-article-date__date-time')

        if date_tag:
            raw_date = date_tag.get_text(strip=True).replace(', UK', '')

            parsed_date = datetime.strptime(raw_date, "%A %d %B %Y %H:%M")

            uk_timezone = pytz.timezone("Europe/London")
            news_shared_date = uk_timezone.localize(parsed_date)

        #content   
  
        article_text_div = soup.find("div", class_="sdc-article-body")

        if article_text_div:    

            for div in article_text_div.find_all('div', class_='sdc-article-strapline__link'):
                div.decompose()

            for div in article_text_div.find_all('div', class_='sdc-article-related-stories'):
                div.decompose()

            for div in article_text_div.find_all('div', class_='ui-app-promo-container'):
                div.decompose()
                
            for div in article_text_div.find_all('div', class_='sdc-site-share'):
                div.decompose()
                
            for div in article_text_div.find_all('div', class_='sdc-trust-project'):
                div.decompose()

            for div in article_text_div.find_all('video'):
                div.decompose()
                
                
            pattern = re.compile(r"^(READ MORE:|WATCH:)", re.I)
            for strong_tag in soup.find_all("strong"):
                if pattern.match(strong_tag.get_text(strip=True)):
                    strong_tag.find_parent("p").decompose()


            CLASS_MATCHES = {
                'div': [
                    "sdc-site-video",
                    "sdc-article-strapline",
                ],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for fc_tag in article_text_div.find_all('figure'):
                fc_tag.decompose()

            for fc_tag in article_text_div.find_all('gu-island'):
                fc_tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    
