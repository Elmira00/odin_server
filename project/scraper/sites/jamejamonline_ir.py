# rss: https://jamejamonline.ir/fa/rss/1
# region: Iran
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from datetime import datetime
import jdatetime

def persian_to_english(s: str) -> str:
    persian = "۰۱۲۳۴۵۶۷۸۹"
    english = "0123456789"
    return s.translate(str.maketrans(persian, english))

def parse_published_time(soup):
    tag = soup.select_one('meta[property="article:published_time"]')
    if not tag:
        return None
    
    raw_content = tag["content"]  
    raw_content = persian_to_english(raw_content)  

    date_part, time_part = raw_content.split(" - ")
    jy, jm, jd = map(int, date_part.split("/"))
    hour, minute = map(int, time_part.split(":"))

    jalali_date = jdatetime.date(jy, jm, jd)
    gregorian_date = jalali_date.togregorian()

    dt = datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day, hour, minute)

    return timezone.make_aware(dt, timezone.get_default_timezone())


from utils.decorators import check_source_active


@check_source_active("https://jamejamonline.ir/")
def get_news_links_jamejamonline_ir(request=None):
    sitemap_url = Source.objects.get(link="https://jamejamonline.ir/").rss_link
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
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
                    links.append((link))
                    link_set.add(link)

        for link in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_jamejamonline_ir(link)

            process_article_data(
                source_link="https://jamejamonline.ir/",
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


def fetch_article_details_jamejamonline_ir(url):
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
        if not image_url.startswith('https'):
            image_url = 'https://jamejamonline.ir' + image_url

        news_shared_date = parse_published_time(soup)

        # content

        article_text_div = soup.find("section", {'class': 'body'})

        if article_text_div:

            CLASS_MATCHES = {
                "div": ["inline-news-box", 'zxc'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ['https://jamejamonline.ir' + img for img in gallery_images]

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for tag in article_text_div.find_all(['figure', 'header', 'iframe']):
                tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
