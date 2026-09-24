# rss: https://www.1in.am/feed

from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
from datetime import datetime
from django.utils import timezone
import requests
import time

armenian_months = {
    'Հունվար': 'January', 'Փետրվար': 'February', 'Մարտ': 'March',
    'Ապրիլ': 'April', 'Մայիս': 'May', 'Հունիս': 'June',
    'Հուլիս': 'July', 'Օգոստոս': 'August', 'Սեպտեմբեր': 'September',
    'Հոկտեմբեր': 'October', 'Նոյեմբեր': 'November', 'Դեկտեմբեր': 'December'
}

from utils.decorators import check_source_active


@check_source_active("https://www.1in.am/")
def get_news_links_1in_am(request=None):
    sitemap_url = Source.objects.get(link="https://www.1in.am/").rss_link
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
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_1in_am(link)
            if content == "video":
                continue

            process_article_data(
                source_link="https://www.1in.am/",
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


def fetch_article_details_1in_am(url):
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
        if soup.find("div", class_="video-container"):
            return None, None, "video", None, None, None

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        dt = soup.find("div", class_="post_item_date")
        if dt:
            dt = dt.text.strip()
            for arm_month, eng_month in armenian_months.items():
                if arm_month in dt:
                    dt = dt.replace(arm_month, eng_month)
                    break
            naive_datetime = datetime.strptime(dt, '%d %B, %Y %H:%M')
            news_shared_date = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        else:
            news_shared_date = None

        #content

        article_text_div = soup.find("div", class_="single-post-content")

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)

            CLASS_MATCHES = {
                'span': ['news-photo'],
                'div': ['rating-section', 'clearfix']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, {'class': class_name}):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("div", id="adfox_162304789613316169"):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date
