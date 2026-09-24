import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://gunaz.tv/az/")
def get_news_links_gunaz_tv(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://gunaz.tv/az/latest-news"
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://gunaz.tv/az/"

    news_cards = soup.find_all('li', class_='article_item')    

    for news_card in news_cards:
        link = news_card.find("a")["href"]
        rss_image = news_card.find("a").find("img")["src"] if news_card.find("a").find("img") and news_card.find("a").find("img").get("src") else None
        if link and link not in link_set and rss_image:
            links.append((link, rss_image))
            link_set.add(link)

    for link, rss_image in links[:20]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_gunaz_tv(link)
        if image_url is None:
            image_url = rss_image

        process_article_data(
            source_link="https://gunaz.tv/az/",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date
        )
        
    else:
        return None


def fetch_article_details_gunaz_tv(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)

        date_text = soup.find("span", class_="date").get_text(strip=True)
        naive_dt = timezone.datetime.strptime(date_text, "%Y.%m.%d, %H:%M")
        news_shared_date = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        #content

        article_text_div = soup.find("div", {"class": "article_content"})
        if not article_text_div or not article_text_div.get_text(strip=True):
            article_text_div = soup.find("div", class_="bottom_text").find("div", class_="text")

        if article_text_div: 

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
