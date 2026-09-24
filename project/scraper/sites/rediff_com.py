# rss: https://www.rediff.com/rss/newshead.xml
# india

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


def get_news_links_rediff_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.rediff.com/").rss_link
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
            description = item.find("description").get_text(strip=True) if item.find("description") else None
            rss_image = item.find("image").text.strip() if item.find("image") else None

            if link and description and rss_image:
                if link not in link_set:
                    rss_image = "https:" + rss_image if rss_image.startswith("//") else rss_image
                    links.append((link, description, rss_image))
                    link_set.add(link)

        for link, description, rss_image in links[:40]:
            title, content, image_url, gallery_images, news_shared_date = fetch_article_details_rediff_com(link)
            if not content:
                continue
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://www.rediff.com/",
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


def fetch_article_details_rediff_com(url):
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

        title = scrape_meta_title(soup)
        if not title:
            title_tag = soup.find("h1", class_="artihd")
            title = title_tag.get_text(strip=True) if title_tag else None
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find('meta', {'itemprop': 'datePublished'})['content']

        # content

        article_text_div = soup.find("div", {'class': 'arti_contentbig'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ['https:' + img for img in gallery_images if img.startswith('//')]

            CLASS_MATCHES = {
                "div": ["imgcaption", 'clear', 'advtcontainer'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'img']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None
    