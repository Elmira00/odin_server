# region: Germany
import requests
from bs4 import BeautifulSoup
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from datetime import datetime
import re

def parse_datetime_tag(tag):
    dt_str = tag.get("datetime")
    dt_str = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})T', lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}T", dt_str)

    try:
        aware_dt = timezone.make_aware(datetime.fromisoformat(dt_str), timezone.get_current_timezone())
        return aware_dt
    except ValueError as e:
        print("❌ Invalid datetime:", dt_str, e)
        return None


def get_news_links_rsf_org(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://rsf.org/en/news"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://rsf.org"

    news_cards = soup.find_all('a', class_='field-group-link')    

    for news_card in news_cards:
        link = news_card['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:15]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_rsf_org(link)
        process_article_data(
            source_link="https://rsf.org/en",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date
        )
        
    else:
        return None


def fetch_article_details_rsf_org(url):
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

        tag = soup.find("time", class_="date")
        news_shared_date = parse_datetime_tag(tag) if tag else None

        #content

        article_text_div = soup.find("div", {"class": "field--type-entity-reference-revisions"})

        if article_text_div: 

            CLASS_MATCHES = {
                "div": ["wrapper-date", 'wrapper-links-mots-cles', 'paragraph--type--pays-classement'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ["https://rsf.org" + img for img in gallery_images if img.startswith("/")]

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe', 'script']):
                tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None,None, None