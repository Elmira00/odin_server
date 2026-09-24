# rss: https://cursorinfo.co.il/feed/
# region: Israel

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://cursorinfo.co.il/")
def get_news_links_cursorinfo_co_il(request=None):
    sitemap_url = Source.objects.get(link="https://cursorinfo.co.il/").rss_link
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
            content = item.find("content:encoded").get_text(strip=True) if item.find("content:encoded") else None
            content = BeautifulSoup(content, "html.parser") if content else None
            CLASS_MATCHES = {
                "div": ['atf_news_p', 'twitter-tweet'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in content.find_all(tag_name, {'class': class_name}):
                        tag.decompose()
            clean_soup_tags(soup, content)
            content = clean_donya_e_eqtesad_com(content.prettify())
            content = clean_html_withregex(content)
            rss_description = item.find("description").get_text(strip=True) if item.find("description") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None
            rss_image = item.find("enclosure").get("url") if item.find("enclosure") else None

            if link and content and rss_description and rss_date and rss_image:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, content, rss_description, rss_date, rss_image))
                    link_set.add(link)

        for link, content, rss_description, rss_date, rss_image in links[:30]:
            title, description, image_url, gallery_images, news_shared_date = fetch_article_details_cursorinfo_co_il(link)
            if not description:
                description = rss_description
            if not news_shared_date:
                news_shared_date = rss_date
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://cursorinfo.co.il/",
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


def fetch_article_details_cursorinfo_co_il(url):
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
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        
        #updated
        if not image_url:
            news_image_div = soup.find("div", class_="news_image")
            if news_image_div:
                img_tag = news_image_div.find("img")
                if img_tag:
                    image_url = img_tag.get("data-lazy-src") or img_tag.get("src")


                
        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content'] if soup.find('meta', {'property': 'article:published_time'}) else None

        # content

        article_text_div = soup.find("div", {'class': 'news_content'})

        if article_text_div:

            CLASS_MATCHES = {
                "div": ['atf_news_p', 'twitter-tweet'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, {'class': class_name}):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)
            if len(gallery_images) == 1:
                gallery_images = []
            else:
                gallery_images = ["https:" + img for img in gallery_images if img.startswith("//")]

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None
