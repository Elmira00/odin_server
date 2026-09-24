import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://anlatilaninotesi.com.tr/")
def get_news_links_anlatilaninotesi(request):
    sitemap_url = Source.objects.get(link="https://anlatilaninotesi.com.tr/").rss_link
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')        
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            pub_date_raw = item.find('pubDate').text.strip() if item.find('pubDate') else None
            rss_title = item.find('title').text.strip() if item.find('title') else None
            rss_description = item.find('description').text.strip() if item.find('description') else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and pub_date_raw and rss_title and rss_description and rss_image:
                if link not in link_set:
                    dt_baku = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                    links.append((link, dt_baku, rss_title, rss_description, rss_image))
                    link_set.add(link)

        for link, news_shared_date, rss_title, rss_description, rss_image in links[:100]:
            title,description, content, image_url,gallery_images = fetch_article_details_anlatilaninotesi(link)
            if not content:
                continue
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://anlatilaninotesi.com.tr/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        return None
    

def fetch_article_details_anlatilaninotesi(url):
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)        
         
        # CONTENT ALMAK İÇİN
        article_body_div_class = soup.find('div', class_='article__body')

        news_content2 = ""

        if article_body_div_class:

            article_block_div_classes = article_body_div_class.find_all('div', class_='article__block')

            if len(article_block_div_classes) == 1:
                article_block = article_block_div_classes[0]

                if article_block:
                    article_photo_item_div_classes = article_block.find_all('div', class_='article__photo-item')
                    for article_photo in article_photo_item_div_classes:
                        news_content2 += article_photo.prettify()

                parsed_content = BeautifulSoup(news_content2, 'html.parser')
                gallery_images = extract_gallery_images(parsed_content)
                clean_soup_tags(parsed_content, parsed_content)
                content = clean_donya_e_eqtesad_com(parsed_content.prettify())
                content = clean_html_withregex(content)

            else:
                
                for div in article_body_div_class.find_all('div', class_='article__article m-image'):
                    div.decompose()
                gallery_images = extract_gallery_images(article_body_div_class)
                clean_soup_tags(soup, article_body_div_class)
                content = clean_donya_e_eqtesad_com(article_body_div_class.prettify())
                content = clean_html_withregex(content)
                
        else:
            content = None
            
        image_class = soup.find('div', class_='media__size')
        if image_class:
            image = image_class.find('div', class_='photoview__open')
            
            if image:
                image = image.find('img')
                image_url = image['src'] if image else None
            else:
                image_url = None
        else:
            article_photo_item_div_classes = article_body_div_class.find_all('div', class_='article__photo-item')
            if article_photo_item_div_classes:
                
                article_photo = article_photo_item_div_classes[0]
                if article_photo:
                    image = article_photo.find('img')
                    image_url = image['src'] if image else None
                else:
                    image_url = None
            else:
                image_url = None
        if image_url is None:
            image_url = scrape_meta_url(soup)

        if content is None:
            content = soup.find("div", {"itemprop": "articleBody"}).get_text(strip=True) if soup.find("div", {"itemprop": "articleBody"}) else None
                        
        return title, description, content, image_url,gallery_images
    
    else:
        return None, None, None, None,None
