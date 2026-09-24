# rss: https://uk.news.yahoo.com/rss/uk
# region: UK
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://uk.news.yahoo.com/")
def get_news_links_uk_yahoo_com(request=None):
    sitemap_url = Source.objects.get(link="https://uk.news.yahoo.com/").rss_link
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
            rss_image = item.find("media:content")["url"].strip() if item.find("media:content") and item.find("media:content").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:5]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_uk_yahoo_com(link)

            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://uk.news.yahoo.com/",
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


def fetch_article_details_uk_yahoo_com(url):
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
        if not image_url:
            article_tag = soup.find('article')
            
            if article_tag:
                figure_tag = article_tag.find('figure')
                if figure_tag:
                    img_tag = figure_tag.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag['src']
                
                if not image_url:
                    img_tag = article_tag.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag['src']

        news_shared_date = soup.find('time')['datetime']

        # content

        article_text_div = soup.find("div", attrs={"data-article-body": "true"})

        # 2 Yahoo Finance şablonu 
        if not article_text_div:
            article_text_div = soup.find("div", attrs={"data-testid": "article-body"})
            
        # 3 Klassik Yahoo
        if not article_text_div:
            article_text_div = soup.find("div", class_="caas-body")
            
        # 4 Alternativ 
        if not article_text_div:
            article_text_div = soup.find("div", class_="article-body")

        if article_text_div:

            CLASS_MATCHES = {
                "div": ["mb-4", 'bg-marshmallow', 'hidden'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("figure"):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
