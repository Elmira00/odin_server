#rss: https://www.rfi.fr/fa/rss
from DrissionPage import WebPage, ChromiumOptions, SessionPage
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url


from utils.decorators import check_source_active


@check_source_active("https://www.rfi.fr/fa/")
def get_news_links_rfi_fr_fa(request=None):
    sitemap_url = Source.objects.get(link="https://www.rfi.fr/fa/").rss_link

    co = ChromiumOptions()
    co.headless(True)  
    co.mute(True)      
    co.set_user_agent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.7339.127 Safari/537.36"
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

        for link in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_rfi_fr_fa(link, web_page)

            process_article_data(
                source_link="https://www.rfi.fr/fa/",
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


def fetch_article_details_rfi_fr_fa(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('div.t-content__body', timeout=30)
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
        news_shared_date = soup.find("meta", {"property": "article:published_time"})["content"]

        #content

        article_text_div = soup.find("div", class_="t-content__body")

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
