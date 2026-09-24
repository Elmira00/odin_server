# rss: https://www.zdfheute.de/rss/zdf/nachrichten
# region: Germany

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone


def get_news_links_zdfheute_de(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.zdfheute.de/thema/nachrichten-zuletzt-veroeffentlicht-100.html"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://zdfheute.de"

    news_cards = soup.find_all('a', class_='b7kurox f1mro3s7 sm2e8be _nl_')    

    for news_card in news_cards:
        link = news_card['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:48]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_zdfheute_de(link)
        process_article_data(
            source_link="https://www.zdfheute.de/",
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


def fetch_article_details_zdfheute_de(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = "utf-8"

    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None
    news_shared_date = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find('time')['datetime'] if soup.find('time') and soup.find('time').has_attr('datetime') else None

        # content

        article_text_div = soup.find("div", {'class': 'ssqw5rh f1uhhdhr'})

        if article_text_div:

            CLASS_MATCHES = {
                "div": ["ch0g9sk", 'pamiw1k', 'ad-wrapper--mark', 'a1n89n1m'],
                'article': ['bhv9830'],
                'figure': ['ff6tzbu']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()
            
            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = [img for img in gallery_images if img.startswith('http')]

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote", 'svg', 'hr']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None