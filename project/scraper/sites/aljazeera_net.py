# rss: https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone

from utils.decorators import check_source_active


@check_source_active("https://www.aljazeera.net/")
def get_news_links_aljazeera_net(request=None):
    sitemap_url = Source.objects.get(link="https://www.aljazeera.net/").rss_link
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
            if "/video/" in link:
                continue
            if "/liveblog/" in link:
                continue
            if "/lifestyle/" in link:
                continue

            if link:
                if link not in link_set:
                    links.append(link)
                    link_set.add(link)

        for link in links[:25]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_aljazeera_net(link)

            process_article_data(
                source_link="https://www.aljazeera.net/",
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


def fetch_article_details_aljazeera_net(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=5)
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
        news_shared_date = (
            timezone.make_aware(datetime.fromisoformat(tag["content"]), timezone.get_current_timezone())
            if (tag := soup.find("meta", {"name": "publishedDate"})) and tag.has_attr("content")
            else None
        )

        # content

        article_text_div = soup.find("div", {'class': 'wysiwyg--all-content'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ["https://www.aljazeera.net" + img if not img.startswith("http") else img for img in gallery_images]

            CLASS_MATCHES = {
                "div": ["container--ads"],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote", "h2"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
