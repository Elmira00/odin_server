# rss: https://www.mirror.co.uk/news/?service=rss
# region: UK
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re
from dateutil import parser 

from utils.decorators import check_source_active


@check_source_active("https://www.mirror.co.uk/")
def get_news_links_mirror_co_uk(request=None):
    sitemap_url = Source.objects.get(link="https://www.mirror.co.uk/").rss_link
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
            rss_image = item.find("media:content")["url"].strip() if item.find("media:content") and item.find("media:content").get("url") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_description = item.find("description").text.strip() if item.find("description") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None
            if "-live-" in link:
                continue
            if "/gallery/" in link:
                continue

            if link and rss_image and rss_title and rss_description and rss_date:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, rss_image, rss_title, rss_description, rss_date))
                    link_set.add(link)

        for link, rss_image, rss_title, rss_description, rss_date in links[:25]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_mirror_co_uk(link)

            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            news_shared_date = rss_date
            if not content:
                continue

            process_article_data(
                source_link="https://www.mirror.co.uk/",
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


def fetch_article_details_mirror_co_uk(url):
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
        if soup.find("article", class_=re.compile(r"LiveEvents_article-body")):
            return None, None, None, None, None, None

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content']

        # content

        article_text_div = soup.find("article", id="article-body")
        if not article_text_div:
            article_text_div = soup.find("ul", class_="UnorderedList_unordered-list__gzblI")
        if not article_text_div:
            article_text_div = soup.find("ol", class_=re.compile(r"NumberedList_numbered-list"))

        if article_text_div:

            CLASS_MATCHES = {
                "div": ['Byline_byline-container__K_Owl', 'BoxStyles_box-container__Qk3WH',
                        'HtmlEmbed_container__x6svQ', "BoxStyles_box-container__Qk3WH"],
                "section": ["Grid_grid-container__uDzQC"]
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ['ImageEmbed_image-embed__0T8WX'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", 'span']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
