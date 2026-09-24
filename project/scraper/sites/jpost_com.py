# rss: https://www.jpost.com/rss/rssfeedsinternational

from DrissionPage import WebPage, ChromiumOptions
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
from django.utils import timezone
from datetime import datetime

from utils.decorators import check_source_active


@check_source_active("https://www.jpost.com/")
def get_news_links_jpost_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.jpost.com/").rss_link

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

        page.wait.eles_loaded('t:item')

        soup = BeautifulSoup(page.html, "xml")

        if soup:
            items = soup.find_all('item')
            
            links = []
            link_set = set()
            
            for item in items:
                link = item.find('link').text.strip() if item.find('link') else None

                if link :
                    if link not in link_set:
                        links.append((link))
                        link_set.add(link)

        for link in links[:60]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_jpost_com(link, page)

            process_article_data(
                source_link="https://www.jpost.com/",
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


def fetch_article_details_jpost_com(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('section@itemprop="articleBody"')
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
        news_shared_date = (
            timezone.make_aware(datetime.fromisoformat(tag['datetime']), timezone.get_current_timezone())
            if (tag := soup.find('time')) and tag.has_attr('datetime')
            else None
        )

        #content

        article_text_div = soup.find("section", {'itemprop': 'articleBody'})

        if article_text_div:

            CLASS_MATCHES = {
                'section': [
                    'hide-for-premium', 'article-top-story-wrap'
                ]
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images, news_shared_date
