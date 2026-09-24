# rss: https://omannews.gov.om/rss.ona

from DrissionPage import WebPage, ChromiumOptions
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_description,scrape_meta_news_shared_date,scrape_meta_title,scrape_meta_url
from datetime import datetime
from django.utils import timezone


def parse_arabic_date(soup):
    arabic_months = {
        "يناير": "January", "فبراير": "February", "مارس": "March",
        "أبريل": "April", "ابريل": "April", "مايو": "May", "يونيو": "June",
        "يوليو": "July", "أغسطس": "August", "اغسطس": "August",
        "سبتمبر": "September", "أكتوبر": "October", "اكتوبر": "October",
        "نوفمبر": "November", "ديسمبر": "December"
    }

    try:
        tag = soup.find('figcaption', class_='wp-caption-text')
        text = tag.get_text(strip=True) if tag else ""
        for ar, en in arabic_months.items():
            text = text.replace(ar, en)
        dt = datetime.strptime(text, "%d %B %Y")
        return timezone.make_aware(dt, timezone.get_current_timezone())
    except Exception:
        return None


from utils.decorators import check_source_active


@check_source_active("https://omannews.gov.om/")
def get_news_links_omannews_gov_om(request=None):
    sitemap_url = Source.objects.get(link="https://omannews.gov.om/").rss_link

    co = ChromiumOptions()
    co.headless(False)  
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
                link = item.find('link').text.strip() if item.find('link') else None

                if link :
                    if link not in link_set:
                        links.append(link)
                        link_set.add(link)

        for link in links[:100]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_omannews_gov_om(link, page)

            process_article_data(
                source_link="https://omannews.gov.om/",
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


def fetch_article_details_omannews_gov_om(url, page: WebPage):
    new_tab = page.new_tab()
    html = None

    try:
        new_tab.get(url, timeout=60)
        new_tab.wait.eles_loaded('article.post-content')
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
        news_shared_date = parse_arabic_date(soup)

        #content

        article_text_div = soup.find("article", {'class': 'post-content'})

        if article_text_div:

            CLASS_MATCHES = {
                'div': ['widget']
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
