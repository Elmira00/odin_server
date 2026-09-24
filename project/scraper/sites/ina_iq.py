# rss: https://ina.iq/rss.xml

from DrissionPage import WebPage, ChromiumOptions
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://ina.iq/en/")
def get_news_links_ina_iq(request=None):
    sitemap_url = Source.objects.get(link="https://ina.iq/en/").rss_link

    co = ChromiumOptions()
    co.headless(True)  
    co.mute(True)      
    co.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
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
                link = item.find("link").text.strip() if item.find("link") else None
                pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None 

                if link and pub_date_raw:
                    if link not in link_set:
                        dt = parser.parse(pub_date_raw)
                        dt_baku = dt.astimezone(pytz.timezone("Asia/Baku"))
                        
                        links.append((link, dt_baku))
                        link_set.add(link)

        for link, news_shared_date in links[:13]:
            title, description, content, image_url, gallery_images = fetch_article_details_ina_iq(link, page)

            process_article_data(
                source_link="https://ina.iq/en/",
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


def fetch_article_details_ina_iq(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('div#fullStory')
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

        #content

        article_text_div = soup.find("div", {'id': 'fullStory'})

        if article_text_div:

            CLASS_MATCHES = {
                'div': [
                    'tpl-layout__mobile', 'advert', 'advert-container', 'cta', 'teaser',
                    'html-embed'
                ]
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", 'h5']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)

    return title, description, content, image_url, gallery_images
