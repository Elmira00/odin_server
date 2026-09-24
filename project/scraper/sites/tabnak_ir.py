# rss: https://www.tabnak.ir/fa/rss/allnews
# region: Iran
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.tabnak.ir/")
def get_news_links_tabnak_ir(request=None):
    sitemap_url = Source.objects.get(link="https://www.tabnak.ir/").rss_link
    try:
        headers = {
            "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }
        response = requests.get(sitemap_url, headers=headers, timeout=10)
    except requests.ConnectTimeout:
        return None

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
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_tabnak_ir(link)

            process_article_data(
                source_link="https://www.tabnak.ir/",
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


def fetch_article_details_tabnak_ir(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
    except requests.ConnectTimeout:
        return None, None, None, None, None, None

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
            news_main_body = soup.find("div", id="newsMainBody")
            if news_main_body:
                img_tag = news_main_body.find("img", class_="lead_image")
                if img_tag:
                    image_url = img_tag.get("src") or img_tag.get("data-src")
                
        news_shared_date = scrape_meta_news_shared_date(soup)
        if not news_shared_date:
            news_shared_date = soup.find("meta", {"name": "DC.Date.Created"})["content"] if soup.find("meta", {"name": "DC.Date.Created"}) else None
            
        # content

        article_text_div = soup.find("div", {'class': 'body'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("p", {'style': 'text-align:center;'}):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
