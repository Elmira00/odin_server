# rss: https://avatoday.net/taxonomy/term/33/feed
# region: Iran
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone

from utils.decorators import check_source_active


@check_source_active("https://avatoday.net/")
def get_news_links_avatoday_net(request=None):
    sitemap_url = Source.objects.get(link="https://avatoday.net/").rss_link
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

            if link:
                if link not in link_set:
                    links.append((link))
                    link_set.add(link)

        for link in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_avatoday_net(link)

            process_article_data(
                source_link="https://avatoday.net/",
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


def fetch_article_details_avatoday_net(url):
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
        website_base_url = "https://avatoday.net"

        title = soup.find("title").text.strip() if soup.find("title") else None
        description = soup.find("meta", attrs={"name": "description"})['content'].strip() if soup.find("meta", attrs={"name": "description"}) else None
        image_url = website_base_url + soup.find('div', class_='image-default').find('img')['src'] if soup.find('div', class_='entry-content') and soup.find('div', class_='entry-content').find('img') else None
        
        date_str = soup.find("div", class_="date").get_text(" ", strip=True)
        date_str = date_str.replace("posted on", "").strip()
        dt = datetime.strptime(date_str, "%B %d, %Y")
        news_shared_date = timezone.make_aware(dt, timezone.get_current_timezone())

        # content

        article_text_div = soup.find("div", {'class': 'content-main'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = [img if img.startswith('http') else website_base_url + img for img in gallery_images]

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
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
