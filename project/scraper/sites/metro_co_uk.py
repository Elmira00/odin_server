# rss: https://metro.co.uk/feed/
# region: UK
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://metro.co.uk/")
def get_news_links_metro_co_uk(request=None):
    sitemap_url = Source.objects.get(link="https://metro.co.uk/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_content = item.find("content:encoded").text.strip() if item.find("content:encoded") else None
            rss_content = BeautifulSoup(rss_content, "html.parser")
            rss_image = rss_content.find("img")["src"] if rss_content.find("img") and rss_content.find("img").get("src") else None
            if "daily-cartoon" in link:
                continue

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_metro_co_uk(link)
            
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://metro.co.uk/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        None


def fetch_article_details_metro_co_uk(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8"

    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None
    news_shared_date = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content']

        # content

        article_text_div = soup.find("div", attrs={"class": "article__content__inner"})

        # updated
        if not image_url and article_text_div:
            img_wrap = article_text_div.find("div", class_="img-wrap")
            if img_wrap:
                img_tag = img_wrap.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag["src"]
            
        if article_text_div:

            CLASS_MATCHES = {
                "div": ['ad-slot', 'factbox', 'video-player', 'trending-now', 'newsletter-end-card', 'metro-more-from'],
                'p': ['metro-more-link']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()
            

            for ul_class in article_text_div.find_all(["figure", 'span', 'section']):
                ul_class.decompose()
            

            [p.decompose() for p in article_text_div.find_all("p")[-2:]]

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
