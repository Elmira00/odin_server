from datetime import datetime
from bs4 import BeautifulSoup
from django.utils import timezone
from playwright.sync_api import sync_playwright
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url

from utils.decorators import check_source_active


@check_source_active("https://24news.ge/")
def get_news_links_24news_ge(request=None):
    sitemap_url = "https://24news.ge/"

    links = []
    link_set = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        ) 
        page = browser.new_page()
        page.goto(sitemap_url, timeout=30000, wait_until="domcontentloaded")

        page.wait_for_selector("div.news-i")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        for a_tag in soup.find_all("a", class_="news-i-inner", href=True):
            href = a_tag["href"]
            if href not in link_set:
                links.append(sitemap_url + href)
                link_set.add(href)

        browser.close()

    for link in links[:24]:
        title, description, content, image_url, gallery_images, news_shared_date = (
            fetch_article_details_24news_ge(link)
        )
        process_article_data(
            source_link="https://24news.ge/",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date,
        )

    else:
        return None


def fetch_article_details_24news_ge(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        resp = page.goto(url, timeout=60000, wait_until="domcontentloaded")

        try:
            page.wait_for_selector(
                "article, .content, .post, .single-news", timeout=10000
            )
        except Exception:
            pass

        html = page.content()
        browser.close()

    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None
    news_shared_date = None

    if html:
        soup = BeautifulSoup(html, "html.parser")

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        MONTHS = {
            "Yan": 1, "Fev": 2, "Mar": 3, "Apr": 4, "May": 5, "İyn": 6,
            "İyl": 7, "Avq": 8, "Sen": 9, "Okt": 10, "Noy": 11, "Dek": 12
        }

        day = soup.find("div", class_="date-day").get_text(strip=True)
        month_text = soup.find("div", class_="date-month").get_text(strip=True)
        year = soup.find("div", class_="date-year").get_text(strip=True)
        time_str = soup.find("div", class_="when-time").get_text(strip=True)

        month = MONTHS[month_text]
        date_str = f"{day}-{month}-{year} {time_str}"
        naive_dt = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
        news_shared_date = timezone.make_aware(naive_dt, timezone.get_default_timezone())

        # content

        article_text_div = soup.find("text", id="textarea")

        if article_text_div:
            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all(
                "ul", class_="gallery_attach_list"
            ):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["header", "footer"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
