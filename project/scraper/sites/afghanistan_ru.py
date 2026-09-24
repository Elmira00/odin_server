# rss: https://afghanistan.ru/feed
# Afghanistan

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone


def get_news_links_afghanistan_ru(request=None):
    sitemap_url = Source.objects.get(link="https://afghanistan.ru/").rss_link
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

            if link and 'station' not in link:
                if link not in link_set:
                    links.append(link)
                    link_set.add(link)

        for link in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_afghanistan_ru(link)

            process_article_data(
                source_link="https://afghanistan.ru/",
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


def fetch_article_details_afghanistan_ru(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8"

    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None
    news_shared_date = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find('h1', {'class': 'head'}).get_text(strip=True)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        date_text = soup.find("span", class_="fl").get_text(strip=True).replace("Опубликовано:", "").strip()
        naive_dt = datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        news_shared_date = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        # content

        article_text_div = soup.find("div", {'class': 'posts'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ["code-block", 'main_img'],
                'p': ['date', 'post_bottom']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'img', 'br', 'center']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None