#rss: https://rustavi2.ge/ka/rss
from DrissionPage import WebPage, ChromiumOptions, SessionPage
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
from datetime import datetime
from django.utils import timezone

from utils.decorators import check_source_active


@check_source_active("https://rustavi2.ge/")
def get_news_links_rustavi2_ge(request=None):
    sitemap_url = "https://rustavi2.ge/en/news"
    website_base_url = "https://rustavi2.ge"

    co = ChromiumOptions()
    co.headless(True)  
    co.mute(True)      
    co.set_user_agent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.7339.127 Safari/537.36"
    )
    co.set_argument('--window-size', '800,600')

    page = None
    try:
        page = WebPage(chromium_options=co)
        page.get(sitemap_url)

        page.wait.eles_loaded('div.nw_line')

        soup = BeautifulSoup(page.html, "html.parser")

        if soup:
            items = soup.find_all('div', class_='news_info')
            
            links = []
            link_set = set()
            
            for item in items:
                link = item.find('a')['href']

                if link:
                    if link not in link_set:
                        links.append((website_base_url + link))
                        link_set.add(link)

        for link in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_rustavi2_ge(link, page)

            process_article_data(
                source_link="https://rustavi2.ge/",
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


def fetch_article_details_rustavi2_ge(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('t:span@itemprop=articleBody', timeout=30)
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

        content_str = soup.find("div", {"itemprop": "datePublished"})["content"]
        dt = datetime.fromisoformat(content_str)
        news_shared_date = timezone.make_aware(dt, timezone.get_current_timezone())

        #content

        article_text_div = soup.find("span", {'itemprop': 'articleBody'})

        if article_text_div:

            CLASS_MATCHES = {
                'div': [
                    'm-interstitial',
                    'o-self-promo',
                ]
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

    return title, description, content, image_url, gallery_images, news_shared_date
