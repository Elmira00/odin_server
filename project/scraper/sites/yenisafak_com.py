# rss: https://www.yenisafak.com/rss-feeds?category=dunya
import json
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://www.yenisafak.com/")
def get_news_links_yenisafak(request):
    sitemap_url = Source.objects.get(link="https://www.yenisafak.com/").rss_link
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
            link = item.find("atom:link")["href"] if item.find("atom:link") else None
            if "/video-galeri/" in link:
                continue
            if "/foto-galeri/" in link:
                continue

            rss_image = item.find("image").find("url").text.strip() if item.find("image") and item.find("image").find("url") else None

            news_shared_date = item.find("pubDate").text.strip() if item.find("pubDate") else None
            news_shared_date = news_shared_date.replace("GMT+3", "+03:00")

            content = item.find("content:encoded").get_text(strip=True) if item.find("content:encoded") else None
            content = BeautifulSoup(content, "html.parser") if content else None
            clean_soup_tags(soup, content)
            content = clean_donya_e_eqtesad_com(content.prettify())
            content = clean_html_withregex(content)

            if link and news_shared_date and content and rss_image:
                if link not in link_set:
                    news_shared_date = parser.parse(news_shared_date)
                    links.append((link, news_shared_date, content, rss_image))
                    link_set.add(link)

        for link, news_shared_date, content, rss_image in links[:30]:
            title, description, image_url, gallery_images = fetch_article_details_yenisafak(link)

            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://www.yenisafak.com/",
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
    

def fetch_article_details_yenisafak(url):
    headers =  {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

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
                
        news_content_div = soup.find('div', class_='ys-detail-content-area')
        news_content_div = news_content_div if news_content_div else soup.find('div', class_='ys-detail-content')
        if news_content_div:
            relateds = news_content_div.find_all('div', class_="ys-related-content-node")
            for related in relateds:
                related.decompose()

            br_classes = news_content_div.find_all('br', class_='ys-new-line-node')
            for br in br_classes:
                br.decompose()

            gallery_images = extract_gallery_images(news_content_div)
            clean_soup_tags(soup, news_content_div)
            content = clean_donya_e_eqtesad_com(news_content_div.prettify())
            content = clean_html_withregex(content)

        elif soup.find('div', class_='content-detail-info'): 
            content_list = []
            content_detail_info = soup.find('div', class_="content-detail-info")
            if content_detail_info:
                image_items = content_detail_info.find_all("div", class_='detail-page-gallery-image')
                for image_item in image_items:

                    for related in image_item.find_all('div', class_="ys-related-content-node"):
                        related.decompose()

                    gallery_images = extract_gallery_images(image_item)
                    content_list.append(image_item.get_text(strip=True))
                raw_content = "\n".join(content_list)
                soup_inner = BeautifulSoup(raw_content, "html.parser")
                container = soup_inner.body or soup_inner
                clean_soup_tags(soup_inner, container)

                content = clean_donya_e_eqtesad_com(str(container))
                content = clean_html_withregex(content)

        elif soup.find("div", class_="content-wrapper"):
            content_lisst = []
            content_wrapper = soup.find("div", class_="content-wrapper")
            if content_wrapper:
                div_co_class = content_wrapper.find("div", class_="content-col")
                if div_co_class:
                    content_details = div_co_class.find_all("div", class_='content-detail-content')
                    for content_detail in content_details:
                        image = content_detail.find('img')
                        image_url = image.get('src') if image and image.has_attr('src') else None

                        gallery_images = extract_gallery_images(content_detail)
                    raw_content = "\n".join(content_lisst)
                    soup_inner = BeautifulSoup(raw_content, "html.parser")
                    container = soup_inner.body or soup_inner
                    clean_soup_tags(soup_inner, container)

                    content = clean_donya_e_eqtesad_com(str(container))
                    content = clean_html_withregex(content)
        else:
            content = None

        image_url = scrape_meta_url(soup)
        if not image_url:
            image_tag = soup.find("div", class_="cover-image").find("img") if soup.find("div", class_="cover-image") else None
            image_url = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

        gallery_images = [
            url for url in gallery_images
            if not url.lower().endswith((".gif", ".svg"))
        ]

        # Tarih Alma
        meta_tag = soup.find("meta", {"name": "datePublished"})
        if meta_tag:
            news_shared_date = meta_tag["content"]
        else:
            meta_tag = soup.find("meta", {"itemprop": "datePublished"})
            if meta_tag:
                news_shared_date = meta_tag["content"]
        if not news_shared_date:
            script = soup.find("script", {"type": "application/ld+json"})

            if script:
                data = json.loads(script.string)
                news_shared_date = data.get("datePublished")

        return title, description, image_url, gallery_images
    else:
        return None, None, None, None
