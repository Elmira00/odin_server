# import requests
# from bs4 import BeautifulSoup
# from scraper.models import NewsArticle,ChangedNewsArticle,Source
# from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
# from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
# from utils.process_article import process_article_data
# from dateutil import parser

# from utils.decorators import check_source_active


# @check_source_active("https://lent.az/")
# def get_news_links_lent(request):
#     sitemap_url = Source.objects.get(link="https://lent.az/").rss_link
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
#     response = requests.get(sitemap_url, headers=headers, timeout=10)
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'xml')
#         items = soup.find_all('item')

#         links = []
#         link_set = set()

#         for item in items:
#             link = item.find("link").text.strip()[:-1] if item.find("link") else None
#             if "/videolent/" in link:
#                 continue
#             pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

#             if link and pub_date_raw:
#                 if link not in link_set:
#                     dt = parser.parse(pub_date_raw)
                    
#                     links.append((link, dt))
#                     link_set.add(link)
        
#         for link, news_shared_date in links[:30]:
#             title, description, content, image_url, gallery_images = fetch_article_details_lent(link)
#             if content is None:
#                 continue

#             process_article_data(
#                 source_link="https://lent.az/",
#                 link=link,
#                 title=title,
#                 description=description,
#                 content=content,
#                 image_url=image_url,
#                 gallery_images=gallery_images,
#                 news_shared_date=news_shared_date,
#             )
#     else:
#         return None
    
    
# def fetch_article_details_lent(url):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
#     response = requests.get(url, headers=headers, timeout=10)
#     response.encoding = 'utf-8'  
   
#     title = None
#     description = None
#     content = None
#     gallery_images = [] 
#     image_url = None
#     news_shared_date = None
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         title = scrape_meta_title(soup)
#         description = scrape_meta_description(soup)

#         content_element = soup.find('div', class_='news_info')
#         if content_element:
#             news_content = content_element.find('div', class_='news_content',itemprop='articleBody')
#             if news_content:
                
#                 gallery_images = extract_gallery_images(news_content)
#                 clean_soup_tags(soup, news_content)
#                 content = clean_donya_e_eqtesad_com(news_content.prettify())
#                 content = clean_html_withregex(content)
#             else:
#                 content = None
#         else:
#             content = None
        
#         image_url = scrape_meta_url(soup)

#         #eger image bosh gelirse body'de axtarsin
        
#         if not image_url:
#             img_div = soup.find('div', class_='news_img')
#             if img_div:
#                 img_tag = img_div.find('img')
#                 if img_tag and img_tag.get('src'):
#                     image_url = img_tag['src']
            
#         # date_div = soup.find('div', class_='overlay')
#         # if date_div:
#         #     date_span = date_div.find('span')
#         #     if date_span:
#         #         date_str = date_span.get_text(strip=True)
                
#         #         date_str = date_str.split('(')[0].strip()

#         #         try:
#         #             month_map = {
#         #                 'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4, 'may': 5,
#         #                 'iyun': 6, 'iyul': 7, 'avqust': 8, 'sentyabr': 9, 'oktyabr': 10,
#         #                 'noyabr': 11, 'dekabr': 12
#         #             }

#         #             date_parts = date_str.split()
#         #             day = date_parts[0]
#         #             month_name = date_parts[1].lower()
#         #             year = date_parts[2]
#         #             time_str = date_parts[3]

#         #             month = month_map.get(month_name)

#         #             if month:
#         #                 formatted_date = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time_str}"
#         #                 news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
#         #             else:
#         #                 news_shared_date = None
#         #         except Exception as e:
#         #             news_shared_date = None
#         #     else:
#         #         news_shared_date = None
#         # else:
#         #     news_shared_date = None

#         return title, description, content, image_url, gallery_images
#     else:
#         return None, None, None, None, None


import logging
import requests
from bs4 import BeautifulSoup
from dateutil import parser

from scraper.models import NewsArticle, ChangedNewsArticle, Source
from utils.clean_content import clean_html_withregex, clean_soup_tags, clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title, scrape_meta_description, scrape_meta_url, scrape_meta_news_shared_date
from utils.process_article import process_article_data
from utils.decorators import check_source_active

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}


@check_source_active("https://lent.az/")
def get_news_links_lent(request):
    try:
        sitemap_url = Source.objects.get(link="https://lent.az/").rss_link
        response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Lent.az RSS/Sitemap çəkilərkən xəta baş verdi: {e}")
        return None
    except Source.DoesNotExist:
        logger.error("Lent.az üçün Source obyekti tapılmadı.")
        return None

    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')

    links = []
    link_set = set()

    for item in items:
        link_tag = item.find("link")
        link = link_tag.text.strip()[:-1] if link_tag else None

        if not link or "/videolent/" in link:
            continue

        pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

        if pub_date_raw and link not in link_set:
            try:
                dt = parser.parse(pub_date_raw)
                links.append((link, dt))
                link_set.add(link)
            except Exception as e:
                logger.warning(f"Tarix parse edilə bilmədi ({pub_date_raw}): {e}")

    for link, news_shared_date in links[:30]:
        title, description, content, image_url, gallery_images = fetch_article_details_lent(link)
        
        # Əgər məqalə təfərrüatları çəkilə bilmədisə və ya content yoxdursa atla
        if content is None:
            continue

        process_article_data(
            source_link="https://lent.az/",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date,
        )


def fetch_article_details_lent(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.warning(f"Lent.az URL cavab vermədi ({response.status_code}): {url}")
            return None, None, None, None, None

    except requests.exceptions.RequestException as e:
        logger.warning(f"Lent.az məqaləsi çəkilərkən bağlantı/timeout xətası ({url}): {e}")
        return None, None, None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    title = scrape_meta_title(soup)
    description = scrape_meta_description(soup)

    content_element = soup.find('div', class_='news_info')
    if content_element:
        news_content = content_element.find('div', class_='news_content', itemprop='articleBody')
        if news_content:
            gallery_images = extract_gallery_images(news_content)
            clean_soup_tags(soup, news_content)
            content = clean_donya_e_eqtesad_com(news_content.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
    else:
        content = None

    image_url = scrape_meta_url(soup)

    if not image_url:
        img_div = soup.find('div', class_='news_img')
        if img_div:
            img_tag = img_div.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']

    return title, description, content, image_url, gallery_images