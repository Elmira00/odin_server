# rss: https://www.rt.com/rss/
# rusiya

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser


def get_news_links_rt_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.rt.com/").rss_link
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
            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 
            rss_description = item.find("description").get_text(strip=True) if item.find("description") else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_content = item.find("content:encoded").text.strip() if item.find("content:encoded") else None

            if link and pub_date_raw and rss_description and rss_title and rss_content and rss_image:
                if link not in link_set:
                    dt = parser.parse(pub_date_raw)
                    dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    
                    rss_description = BeautifulSoup(rss_description, "html.parser")
                    rss_description.find("img").decompose() if rss_description.find("img") else None
                    rss_description.find("a").decompose() if rss_description.find("a") else None
                    
                    links.append((link, dt_baku, rss_description, rss_title, rss_content, rss_image))
                    link_set.add(link)

        for link, news_shared_date, rss_description, rss_title, rss_content, rss_image in links[:20]:
            title, description, content, image_url, gallery_images = fetch_article_details_rt_com(link)
            
            if not description:
                continue
            if not title:
                title = rss_title
            if not content:
                content = rss_content
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://www.rt.com/",
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


def fetch_article_details_rt_com(url):
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
        if description is None:
            description = soup.find("div", class_="article__summary").get_text(strip=True) if soup.find("div", class_="article__summary") else None
        image_url = scrape_meta_url(soup)

        # content

        article_text_div = soup.find('div', {'class': 'article__text'})

        if article_text_div:

            CLASS_MATCHES = {
                "div": ['rtcode', 'Read-more-text-only', 'read-more'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("div", class_="article__cover"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'hr', 'svg', 'style']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images
    else:
        return None, None, None, None, None
    