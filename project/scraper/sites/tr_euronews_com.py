from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url

from utils.decorators import check_source_active


@check_source_active("https://tr.euronews.com/")
def get_news_links_tr_euronews_com(request=None):
    sitemap_url = "https://tr.euronews.com/son-haberler"

    links = []
    link_set = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )  
        page = browser.new_page()
        page.goto(sitemap_url, timeout=30000, wait_until="domcontentloaded")

        page.wait_for_selector("a.c-timeline-items__article__link")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        news_cards = soup.find_all('a', class_='c-timeline-items__article__link')    

        for news_card in news_cards:
            href = news_card.get('href')  
            if href and href not in link_set:
                links.append(href)
                link_set.add(href)

        browser.close()

    for link in links[:15]:
        title, description, content, image_url, gallery_images, news_shared_date = (
            fetch_article_details_tr_euronews_com(link)
        )
        process_article_data(
            source_link="https://tr.euronews.com/",
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


def fetch_article_details_tr_euronews_com(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://tr.euronews.com/",
                "Connection": "keep-alive",
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
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find("meta", {"name": "article:published_time"})["content"]

        # content

        article_text_div = soup.find("div", class_="c-article-content js-article-content")

        if article_text_div:

            CLASS_MATCHES = {
                'div': [
                    "c-ad", "connatix-container", "optidigital-wrapper-div", 
                    "widget", "c-widget-related"
                ],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose() 

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
