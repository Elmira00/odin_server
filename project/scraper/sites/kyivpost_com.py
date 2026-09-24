# # rss: https://www.kyivpost.com/feed
# # rusiya

# from bs4 import BeautifulSoup
# import requests
# from scraper.models import Source
# from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
# from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
# from utils.process_article import process_article_data
# import pytz
# from dateutil import parser


# def get_news_links_kyivpost_com(request=None):
#     sitemap_url = Source.objects.get(link="https://www.kyivpost.com/").rss_link
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
#             if not "/post/" in link:
#                 continue

#             pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

#             if link and pub_date_raw:
#                 if link not in link_set:
#                     dt = parser.parse(pub_date_raw)
#                     dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    
#                     links.append((link, dt_baku))
#                     link_set.add(link)

#         for link, news_shared_date in links[:40]:
#             title, description, content, image_url, gallery_images = fetch_article_details_kyivpost_com(link)

#             process_article_data(
#                 source_link="https://www.kyivpost.com/",
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


# def fetch_article_details_kyivpost_com(url):
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

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")

#         title = scrape_meta_title(soup)
#         if not title:
#             title_tag = soup.find("h1", class_="post-title")
#             title = title_tag.get_text(strip=True) if title_tag else None
#         description = scrape_meta_description(soup)
#         if not description:
#             description_tag = soup.find("p", class_="post-lead")
#             description = description_tag.get_text(strip=True) if description_tag else None
#         image_url = scrape_meta_url(soup)

#         # content

#         article_text_div = soup.find('div', {'id': 'post-content'})

#         if article_text_div:

#             CLASS_MATCHES = {
#                 "div": ['row', 'clear', 'inarticle_link_block', 'ad_between_paragraphs'],
#                 'section': ['tweet']
#             }
#             for tag_name, class_list in CLASS_MATCHES.items():
#                 for class_name in class_list:
#                     for tag in article_text_div.find_all(tag_name, class_=class_name):
#                         tag.decompose()

#             gallery_images = extract_gallery_images(article_text_div)

#             for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
#                 ul_class.decompose()

#             for ul_class in article_text_div.find_all("p", class_="single-image-container"):
#                 ul_class.decompose()

#             for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'hr', 'svg', 'style', 'figcapture']):
#                 ul_class.decompose()

#             clean_soup_tags(soup, article_text_div)
#             content = clean_donya_e_eqtesad_com(article_text_div.prettify())
#             content = clean_html_withregex(content)
#         else:
#             content = None

#         return title, description, content, image_url, gallery_images
#     else:
#         return None, None, None, None, None




# rss: https://www.kyivpost.com/feed
# rusiya

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex, clean_soup_tags, clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title, scrape_meta_description, scrape_meta_url, scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser


def get_news_links_kyivpost_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.kyivpost.com/").rss_link
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            if not link or "/post/" not in link:
                continue

            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

            if link and pub_date_raw:
                if link not in link_set:
                    dt = parser.parse(pub_date_raw)
                    dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                    
                    links.append((link, dt_baku))
                    link_set.add(link)

        for link, news_shared_date in links[:40]:
            title, description, content, image_url, gallery_images, is_audio = fetch_article_details_kyivpost_com(link)

            if is_audio:
                print(f"🎧 Audio/Karikatura xəbər tapıldı və iqnor edildi: {link}")
                continue

            process_article_data(
                source_link="https://www.kyivpost.com/",
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


def fetch_article_details_kyivpost_com(url):
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
    is_audio = False
    has_audio_player = False

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = scrape_meta_title(soup)
        if not title:
            title_tag = soup.find("h1", class_="post-title")
            title = title_tag.get_text(strip=True) if title_tag else None
            
        description = scrape_meta_description(soup)
        if not description:
            description_tag = soup.find("p", class_="post-lead")
            description = description_tag.get_text(strip=True) if description_tag else None
            
        image_url = scrape_meta_url(soup)

        if soup.find('div', class_='instaread-audio-player') or soup.find('iframe', class_='instaread-iframe'):
            has_audio_player = True

        article_text_div = soup.find('div', {'id': 'post-content'})

        if article_text_div:
            if not has_audio_player and (article_text_div.find('audio') or article_text_div.find('iframe')):
                has_audio_player = True

            CLASS_MATCHES = {
                "div": ['row', 'clear', 'inarticle_link_block', 'ad_between_paragraphs'],
                'section': ['tweet']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("p", class_="single-image-container"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'hr', 'svg', 'style', 'figcapture']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

            # Audio/Karikatura qərarı (Mətn qısadırsa)
            if has_audio_player and (not content or len(content.strip()) < 80):
                is_audio = True
        else:
            content = None
            if has_audio_player:
                is_audio = True

        if '/podcast/' in url:
            is_audio = True
            
        meta_section = soup.find("meta", {"property": "article:section"})
        if meta_section and 'podcast' in meta_section.get("content", "").lower():
            is_audio = True

        return title, description, content, image_url, gallery_images, is_audio
    else:
        return None, None, None, None, None, False