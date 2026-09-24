# rss: https://am.sputniknews.ru/export/rss2/archive/index.xml
import requests
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags, extract_gallery_images
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://am.sputniknews.ru/")
def get_news_links_am_sputniknews_ru(request):
    sitemap_url = Source.objects.get(link="https://am.sputniknews.ru/").rss_link
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

            if link and description:
                if link not in link_set:
                    links.append((link, description))
                    link_set.add(link)

        for link, description in links[:30]:
            title, content, image_url, gallery_images, news_shared_date = fetch_article_details_am_sputniknews_ru(link)

            process_article_data(
                source_link="https://am.sputniknews.ru/",
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
    
    
def fetch_article_details_am_sputniknews_ru(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers, timeout=10)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find("html", class_="VideoPage"):
            return None, None, None, None, None

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)

        #content     

        article_text_div = soup.find('div', class_='article__body')
        if not article_text_div or not article_text_div.get_text(strip=True):
            article_text_div = soup.find("div", class_="article__announce-text")

        if article_text_div:
            
            for div in article_text_div.find_all('div', class_='article__article m-image'):
                div.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for picture in article_text_div.find_all('picture'):
                picture.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
            
        else:
            content = None

        image_url = scrape_meta_url(soup)

        # Tarix
        meta_tag_date_tag = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_date_tag:
            date_str = meta_tag_date_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None
