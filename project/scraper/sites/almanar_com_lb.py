# rss: https://english.almanar.com.lb/cat/news/rss
# Lebanon

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser


def get_news_links_almanar_com_lb(request=None):
    sitemap_url = Source.objects.get(link="https://english.almanar.com.lb/").rss_link
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
            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

            if link and pub_date_raw:
                if link not in link_set:
                    dt = parser.parse(pub_date_raw)
                    dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    
                    links.append((link, dt_baku))
                    link_set.add(link)

        for link, news_shared_date in links[:10]:
            title, description, content, image_url, gallery_images = fetch_article_details_almanar_com_lb(link)

            process_article_data(
                source_link="https://english.almanar.com.lb/",
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


def fetch_article_details_almanar_com_lb(url):
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

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        image_url = image_url if image_url.startswith('http') else None

        # content

        article_text_div = soup.find('div', {'class': 'article-content'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                "div": ["container--ads"],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images
    else:
        return None, None, None, None, None