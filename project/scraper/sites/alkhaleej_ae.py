#rss: https://www.alkhaleej.ae/section/1177/rss.xml

from DrissionPage import WebPage, ChromiumOptions, SessionPage
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
import re
from datetime import datetime
from django.utils import timezone


months_ar = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4,
    "مايو": 5, "يونيو": 6, "يوليو": 7, "أغسطس": 8,
    "سبتمبر": 9, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12,
}

def parse_date_time(date_text: str, time_text: str):

    m = re.search(r"(\d{1,2})\s+([^\s]+)\s+(\d{4})", date_text)
    if not m:
        raise ValueError(f"Could not parse date: {date_text}")
    day, month_ar, year = m.groups()
    month = months_ar.get(month_ar)
    if not month:
        raise KeyError(f"Unknown Arabic month: {month_ar}")

    m_time = re.search(r"(\d{1,2}):(\d{2})\s*(صباحا|مساء)?", time_text)
    if not m_time:
        raise ValueError(f"Could not parse time: {time_text}")
    hour, minute, meridiem = m_time.groups()
    hour, minute = int(hour), int(minute)

    if meridiem == "مساء" and hour < 12:
        hour += 12
    if meridiem == "صباحا" and hour == 12: 
        hour = 0

    dt_naive = datetime(int(year), month, int(day), hour, minute)
    dt_aware = timezone.make_aware(dt_naive, timezone.get_default_timezone())
    return dt_aware

from utils.decorators import check_source_active


@check_source_active("https://www.alkhaleej.ae/")
def get_news_links_alkhaleej_ae(request=None):
    sitemap_url = Source.objects.get(link="https://www.alkhaleej.ae/").rss_link

    co = ChromiumOptions()
    co.headless(False)  
    co.mute(True)      
    co.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    )
    co.set_argument('--window-size', '800,600')

    session_page = None
    web_page = None

    try:
        session_page = SessionPage()
        session_page.get(sitemap_url)
        
        xml_content = session_page.html
        soup = BeautifulSoup(xml_content, "xml")

        if soup:
            items = soup.find_all('item')
            
            links = []
            link_set = set()
            
            for item in items:
                link = item.find('link').text.strip() if item.find('link') else None

                if link:
                    if link not in link_set:
                        links.append((link))
                        link_set.add(link)

        web_page = WebPage(chromium_options=co)

        for link in links[:50]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_alkhaleej_ae(link, web_page)

            process_article_data(
                source_link="https://www.alkhaleej.ae/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if session_page:
            try:
                session_page.close()
            except:
                pass
        if web_page:
            try:
                web_page.quit()
            except:
                pass


def fetch_article_details_alkhaleej_ae(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('div.article-content-wrapper', timeout=30)
        html = new_tab.html

    except Exception as e:
        print(f"Error fetching {url}: {e}")

    title = description = content = image_url = None
    gallery_images = []
    news_shared_date = None

    if html:
        soup = BeautifulSoup(html, "html.parser")

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        date_div = soup.select_one("div.field--name-node-post-date")
        date_text = date_div.get_text(strip=True) if date_div else None

        time_span = soup.select_one("span.post-time")
        time_text = time_span.get_text(strip=True) if time_span else "00:00"

        news_shared_date = parse_date_time(date_text, time_text)

        #content

        article_text_div = soup.find("div", class_="article-content-wrapper").find("div", class_='clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item')

        if article_text_div:

            CLASS_MATCHES = {
                'div': [
                    'Article_Ad_div-1', 'Article_Ad_div-2', 'Article_Ad_div-3'
                ]
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, id=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date
