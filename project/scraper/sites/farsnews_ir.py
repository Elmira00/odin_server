from bs4 import BeautifulSoup
from DrissionPage import WebPage, ChromiumOptions

from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
from datetime import datetime
from django.utils import timezone

from utils.decorators import check_source_active


@check_source_active("https://farsnews.ir/showcase")
def get_news_links_farsnews_ir(request=None):
    sitemap_url = "https://farsnews.ir/World_eng/posts"

    co = ChromiumOptions()
    co.headless(True)  
    co.mute(True)      
    co.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    )
    co.set_argument('--window-size', '800,600')

    page = None
    try:
        page = WebPage(chromium_options=co)
        page.get(sitemap_url)

        page.wait.eles_loaded('div.n-y292xp')

        soup = BeautifulSoup(page.html, "html.parser")

        if soup:
            items = soup.find_all('a', class_='n-h3v2f0')
            
            links = []
            link_set = set()
            
            for item in items:
                link = item.get('href')

                if link :
                    if link not in link_set:
                        links.append((link))
                        link_set.add(link)

        for link in links[:4]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_farsnews_ir(link, page)

            process_article_data(
                source_link="https://farsnews.ir/showcase",
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
        if page:
            page.quit() 


def fetch_article_details_farsnews_ir(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('div.n-c4q897')
        html = new_tab.html

    except Exception as e:
        print(f"Error fetching {url}: {e}")

    title = description = content = image_url = None
    gallery_images = []
    news_shared_date = None

    if html:
        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h2", class_="n-579c01").find("span").get_text(strip=True)
        description =soup.find("div", class_="n-c4q897").find("span").get_text(strip=True)
        image_url = soup.find("img", class_="rounded-inherit")["src"]
        
        span = soup.find("span", class_="text-gray-600 @text-body ws-nowrap")
        date_str = span.get_text(strip=True)
        dt = datetime.strptime(date_str, "%H:%M - %d %B %Y")
        news_shared_date = timezone.make_aware(dt, timezone.get_current_timezone())

        #content

        article_text_div = soup.find("div", class_="px-post-padding-x pb-2")

        if article_text_div:
            CLASS_MATCHES = {
                'div': [
                    'items-center',
                ]
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            article_text_div.find("div", class_="pt-1 mt-3").decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date
