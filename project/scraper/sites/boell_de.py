# # rss: https://www.boell.de/de/rss.xml
# # region: Germany

# from bs4 import BeautifulSoup
# import requests
# from scraper.models import Source
# from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
# from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
# from utils.process_article import process_article_data
# from datetime import datetime
# from django.utils import timezone


# def get_news_links_boell_de(request=None):
#     sitemap_url = Source.objects.get(link="https://www.boell.de/de").rss_link
#     headers = {
#         "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
#     }
#     response = requests.get(sitemap_url, headers=headers)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, "xml")
#         items = soup.find_all("item")

#         links = []
#         link_set = set()

#         for item in items:
#             link = item.find("link").text.strip() if item.find("link") else None

#             if link:
#                 if link not in link_set:
#                     links.append(link)
#                     link_set.add(link)

#         for link in links[:10]:
#             title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_boell_de(link)

#             process_article_data(
#                 source_link="https://www.boell.de/de",
#                 link=link,
#                 title=title,
#                 description=description,
#                 content=content,
#                 image_url=image_url,
#                 gallery_images=gallery_images,
#                 news_shared_date=news_shared_date,
#             )
#     else:
#         None


# def fetch_article_details_boell_de(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers, timeout=15)
#     response.encoding = "utf-8"

#     title = None
#     description = None
#     content = None
#     gallery_images = []
#     image_url = None
#     news_shared_date = None

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")

#         title = scrape_meta_title(soup)
#         description = scrape_meta_description(soup)
#         image_url = scrape_meta_url(soup)

#         tag = soup.find("div", class_="article__date")
#         news_shared_date = (
#             timezone.make_aware(
#                 datetime.strptime(tag.get_text(strip=True).replace('.', ''), "%d %B %Y"),
#                 timezone.get_current_timezone()
#             )
#             if tag else None
#         )

#         # content

#         article_text_div = soup.find("div", {'class': 'node__content--article'})

#         if article_text_div:

#             CLASS_MATCHES = {
#                 "div": ["article__footer", 'two-click', 'youtube'],
#                 'p': ['article-special-container']
#             }
#             for tag_name, class_list in CLASS_MATCHES.items():
#                 for class_name in class_list:
#                     for tag in soup.find_all(tag_name, class_=class_name):
#                         tag.decompose()
            
#             gallery_images = extract_gallery_images(article_text_div)

#             for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
#                 ul_class.decompose()

#             for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote"]):
#                 ul_class.decompose()

#             clean_soup_tags(soup, article_text_div)
#             content = clean_donya_e_eqtesad_com(article_text_div.prettify())
#             content = clean_html_withregex(content)
#         else:
#             content = None

#         return title, description, content, image_url, gallery_images, news_shared_date
#     else:
#         return None, None, None, None, None, None




from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from datetime import datetime
from django.utils import timezone
from scraper.models import Source
from utils.clean_content import clean_html_withregex, clean_soup_tags, clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title, scrape_meta_description, scrape_meta_url, scrape_meta_news_shared_date
from utils.process_article import process_article_data

GERMAN_MONTHS = {
    "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
    "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
}

def parse_german_date(date_str):
    try:
        parts = date_str.replace('.', '').strip().split()
        if len(parts) == 3:
            day = int(parts[0])
            month = GERMAN_MONTHS.get(parts[1])
            year = int(parts[2])
            if month:
                naive_dt = datetime(year, month, day)
                return timezone.make_aware(naive_dt, timezone.get_current_timezone())
    except Exception:
        pass
    return None


def get_news_links_boell_de(request=None):
    source_obj = Source.objects.filter(link="https://www.boell.de/de").first()
    if not source_obj or not source_obj.rss_link:
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(source_obj.rss_link, headers=headers, timeout=15)
    except requests.exceptions.RequestException:
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            if link and link not in link_set:
                links.append(link)
                link_set.add(link)

        for link in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_boell_de(link)

            if title or content:
                process_article_data(
                    source_link="https://www.boell.de/de",
                    link=link,
                    title=title,
                    description=description,
                    content=content,
                    image_url=image_url,
                    gallery_images=gallery_images,
                    news_shared_date=news_shared_date,
                )


def fetch_article_details_boell_de(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"
    except requests.exceptions.RequestException:
        return None, None, None, None, None, None

    if response.status_code != 200:
        return None, None, None, None, None, None

    soup = BeautifulSoup(response.text, "html.parser")

    title = scrape_meta_title(soup)
    description = scrape_meta_description(soup)
    image_url = scrape_meta_url(soup)
    
    if image_url:
        image_url = urljoin(url, image_url)

    tag = soup.find("div", class_="article__date")
    news_shared_date = scrape_meta_news_shared_date(soup)

    # Fallback date if main container is missing
    if not news_shared_date:
        news_shared_date = parse_german_date(tag.get_text()) if tag else None

    article_text_div = soup.find("div", class_="node__content--article")

    gallery_images = []
    content = None

    if article_text_div:
        raw_gallery = extract_gallery_images(article_text_div)
        gallery_images = [urljoin(url, img) for img in raw_gallery if img]

        CLASS_MATCHES = {
            "div": ["article__footer", "two-click", "youtube"],
            "p": ["article-special-container"]
        }
        
        # Scope decomposition strictly to the article node
        for tag_name, class_list in CLASS_MATCHES.items():
            for class_name in class_list:
                for target_tag in article_text_div.find_all(tag_name, class_=class_name):
                    target_tag.decompose()

        for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
            ul_class.decompose()

        for media_tag in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote"]):
            media_tag.decompose()

        clean_soup_tags(soup, article_text_div)
        content = clean_donya_e_eqtesad_com(article_text_div.prettify())
        content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date