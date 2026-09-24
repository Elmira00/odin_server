# rss: https://eghtesadepooya.ir/?feed=rss2
# iran

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone


def get_news_links_eghtesadepooya_ir(request=None):
    sitemap_url = Source.objects.get(link="https://eghtesadepooya.ir/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None

            if link:
                if link not in link_set:
                    links.append(link)
                    link_set.add(link)

        for link in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_eghtesadepooya_ir(link)

            process_article_data(
                source_link="https://eghtesadepooya.ir/",
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


def fetch_article_details_eghtesadepooya_ir(url):
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

        tag = soup.find('meta', {'property': 'article:published_time'})
        news_shared_date = tag['content'] if tag and tag.has_attr('content') else None

        # content

        article_text_div = soup.find("div", {'class': 'con'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ["related-news"],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, id=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'svg', 'style']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None