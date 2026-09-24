import requests
from bs4 import BeautifulSoup
from scraper.models import Source

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://www.sondakika.com/")
def get_news_links_sondakika_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.sondakika.com/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("media:content")["url"].strip() if item.find("media:content") and item.find("media:content").get("url") else None
            rss_title = item.find("title").text.strip() if item.find("title") else None
            rss_description = item.find("description").text.strip() if item.find("description") else None
            rss_date = item.find("pubDate").text.strip() if item.find("pubDate") else None

            if link and rss_image and rss_title and rss_description and rss_date:
                if link not in link_set:
                    rss_date = parser.parse(rss_date)
                    links.append((link, rss_image, rss_title, rss_description, rss_date))
                    link_set.add(link)

        for link, rss_image, rss_title, rss_description, rss_date in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_sondakika_com(link)
            if not content:
                continue
            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            if not news_shared_date:
                news_shared_date = rss_date

            process_article_data(
                source_link="https://www.sondakika.com/",
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


def fetch_article_details_sondakika_com(url):
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
        #
        if not image_url:
            img_tag = soup.find('img', id='haberResim')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
            else:
                img_div = soup.find('div', class_='haberResim')
                if img_div:
                    img_tag_alt = img_div.find('img')
                    if img_tag_alt and img_tag_alt.get('src'):
                        image_url = img_tag_alt['src']
        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content']

        #content

        article_text_div = soup.find("div", {"class": "haber_metni"})

        if article_text_div: 


            CLASS_MATCHES = {
                "div": ["comment-container", 'lnkSeo', 'drimg'],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()
                        
            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for ul_class in article_text_div.find_all('div', {'id': 'tb-inpage-general'}):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "style"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
