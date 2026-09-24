from datetime import datetime
from bs4 import BeautifulSoup
from django.utils import timezone
from playwright.sync_api import sync_playwright
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url

from utils.decorators import check_source_active


@check_source_active("https://www.interpressnews.ge/en/")
def get_news_links_interpressnews_ge(request=None):
    sitemap_url = "https://www.interpressnews.ge/en/latestnews"
    website_base_url = "https://www.interpressnews.ge"

    links = []
    link_set = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
            },
        )
        page = context.new_page()
        page.goto(sitemap_url, timeout=30000, wait_until="domcontentloaded")

        page.wait_for_selector("div.categoryitemtitle")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        for div in soup.find_all("div", class_="categoryitemtitle"):
            a_tag = div.find("a", href=True)
            href = a_tag["href"]
            if href not in link_set:
                links.append(website_base_url + href)
                link_set.add(href)

        browser.close()

    for link in links[:15]:
        title, description, content, image_url, gallery_images, news_shared_date = (
            fetch_article_details_interpressnews_ge(link)
        )
        process_article_data(
            source_link="https://www.interpressnews.ge/en/",
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


def fetch_article_details_interpressnews_ge(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.interpressnews.ge/en/latestnews",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        page = context.new_page()
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
        div = soup.find("div", class_="articleimg")
        image_url = div.img["src"] if div and div.img else None


        date_text = soup.find("div", class_="articledate").span.get_text(strip=True)
        date_obj = datetime.strptime(date_text, "%d.%m.%Y / %H:%M")
        news_shared_date = timezone.make_aware(date_obj, timezone.get_default_timezone())

        # content

        article_text_div = soup.find("div", class_="articlecontent_in")

        if article_text_div:
            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
