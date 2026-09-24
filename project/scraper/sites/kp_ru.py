# region: Rusiya
# https://www.kp.ru/rss/allsections.xml

import requests
from bs4 import BeautifulSoup
from scraper.models import Source

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from dateutil import parser


def get_news_links_kp_ru(request=None):
    sitemap_url = Source.objects.get(link="https://www.kp.ru/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("media:content")["url"].strip() if item.find("media:content") and item.find("media:content").get("url") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None
            rss_description = item.find("description").text.strip() if item.find("description") else None

            if link and rss_image and rss_title and rss_date and rss_description:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, rss_image, rss_title, rss_date, rss_description))
                    link_set.add(link)

        for link, rss_image, rss_title, rss_date, rss_description in links[:20]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_kp_ru(link)
            if title == "cartoon":
                continue

            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            if not news_shared_date:
                news_shared_date = rss_date

            process_article_data(
                source_link="https://www.kp.ru/",
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


def fetch_article_details_kp_ru(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers, timeout=10)
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
        if "CARTOON" in title:
            return "cartoon", None, None ,None,None, None
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content']

        #content

        article_text_div = soup.find("div", {"data-gtm-el": "content-body"})

        if article_text_div: 

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = [img for img in gallery_images if ".gif" not in img]

            CLASS_MATCHES = {
                "div": ["sc-1a8tb7h-0", 'sc-1wayp1z-2'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe', 'script', 'picture']):
                tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None