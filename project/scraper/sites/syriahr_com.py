# rss: https://www.syriahr.com/feed/

import subprocess
import time
import requests
from bs4 import BeautifulSoup
from DrissionPage import WebPage, ChromiumOptions
from scraper.models import Source
from utils.clean_content import (
    clean_donya_e_eqtesad_com,
    clean_html_withregex,
    clean_soup_tags,
    extract_gallery_images
)
from utils.process_article import process_article_data
from utils.scrape_content_metatag import (
    scrape_meta_description,
    scrape_meta_news_shared_date,
    scrape_meta_title,
    scrape_meta_url
)


def start_chrome():
    """Chrome'u remote debugging port ile başlat"""
    cmd = [
        "/usr/bin/google-chrome",
        "--remote-debugging-port=9222",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--headless=new",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

from utils.decorators import check_source_active


@check_source_active("https://www.syriahr.com/")
def get_news_links_syriahr_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.syriahr.com/").rss_link

    # Chrome başlat
    chrome_proc = start_chrome()
    time.sleep(3)  # Chrome ayağa kalksın

    # Chromium Options
    co = ChromiumOptions()
    co.set_browser_path("/usr/bin/google-chrome")
    co.set_user_data_path("/tmp/chrome_user_data")  # her instance için ayrı olabilir
    
    co.headless(True)
    co.mute(True)
    co.set_user_agent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    co.set_argument('--window-size', '800,600')

    web_page = None

    try:
        # RSS'i requests ile çek
        headers = {"User-Agent": co.user_agent}
        try:
            resp = requests.get(sitemap_url, headers=headers, timeout=30)
            resp.raise_for_status()
            xml_content = resp.content
        except Exception as e:
            print(f"Requests failed with {e}, trying Chromium fallback...")
            page = WebPage(chromium_options=co)
            page.get(sitemap_url)
            xml_content = page.html
            page.quit()

        soup = BeautifulSoup(xml_content, "xml")
        items = soup.find_all('item')

        links = []
        link_set = set()
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            if link and link not in link_set:
                links.append(link)
                link_set.add(link)

        # WebPage Chromium başlat
        web_page = WebPage(chromium_options=co)

        # İlk 30 haber linkini işleme sok
        for link in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_syriahr_com(link, web_page)

            process_article_data(
                source_link="https://www.syriahr.com/",
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
        if web_page:
            try:
                web_page.quit()
            except:
                pass
        if chrome_proc:
            chrome_proc.terminate()


def fetch_article_details_syriahr_com(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('div.entry-content', timeout=30)
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

        # Yayın tarihi
        published_tag = soup.find("meta", {"property": "article:published_time"})
        if published_tag and published_tag.get("content"):
            news_shared_date = published_tag["content"]

        # İçerik
        article_text_div = soup.find("div", {"class": "entry-content"})

        if article_text_div:
            CLASS_MATCHES = {
                'div': ['ruby-table-contents']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "blockquote"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date
