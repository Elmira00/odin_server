import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active
from zoneinfo import ZoneInfo
from django.utils import timezone
from dateutil import parser


@check_source_active("https://metbuat.az/")
def get_news_links_metbuat(request):
    sitemap_url = Source.objects.get(link="https://metbuat.az/").rss_link
    response = requests.get(sitemap_url, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
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

        for link, rss_image, rss_title, rss_description, rss_date in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_metbuat(link)
            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not news_shared_date:
                news_shared_date = rss_date
            if not description:
                description = rss_description
            
            process_article_data(
                source_link="https://metbuat.az/",
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
    
    
def fetch_article_details_metbuat(url):
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'  
    except requests.ReadTimeout as e:
        return None, None, None, None, None, None

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

        content_element = soup.find('div', class_='wh_box news_in_content')
        if content_element:
            content_inner = content_element.find('article', class_='normal-text')
            if content_inner:
            
                for a_tag in content_inner.find_all('a'):
                    text = a_tag.get_text(strip=True)  
                    if text:  
                        a_tag.string = text + " " 
                        
                for noscript_tag in content_inner.find_all('noscript'):
                    noscript_tag.decompose()
                         
                gallery_images = []
                images = content_inner.find_all('img')

                for image in images: 
                    src = None
                    if image and image.has_attr('data-src'):
                        src = image['data-src'].strip()
                    elif image and image.has_attr('src'):
                        src = image['src'].strip()

                    if src:
                        if src.startswith('/uploads'):
                            src = f"https://metbuat.az{src}"
                        
                        gallery_images.append(src)

                for img in images:
                    img.decompose()
                    
                clean_soup_tags(soup, content_inner)
                content = clean_donya_e_eqtesad_com(content_inner.prettify())
                content = clean_html_withregex(content)       
            else:
                content = None
        else:
            content = None
        
        image_url = scrape_meta_url(soup)
            
        div_class = soup.find('div', class_='gr_box news_in_date_time')
        if div_class:
            news_span = div_class.find('span', class_='news_in_time')
            date_span = div_class.find('span', class_='news_in_date')

            time_str = news_span.get_text(strip=True) if news_span else None
            date_str = date_span.get_text(strip=True) if date_span else None

            if time_str and date_str:
                try:
                    if 'fa' in date_str:
                        date_str = date_str.split()[-3:]  
                    else:
                        date_str = date_str.split()

                    day = date_str[0]
                    month_name = date_str[1].strip().lower()
                    year = date_str[2]

                    month_name = month_name.replace("i̇", "i").replace("İ", "i")

                    month_map = {
                        'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4, 'may': 5,
                        'iyun': 6, 'iyul': 7, 'avqust': 8, 'sentyabr': 9, 'oktyabr': 10,
                        'noyabr': 11, 'dekabr': 12
                    }

                    month = month_map.get(month_name)

                    if month:
                        formatted_date = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time_str}"
                        news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                        news_shared_date = timezone.make_aware(news_shared_date, timezone=ZoneInfo('Asia/Baku'))
                    else:
                        news_shared_date = None
                except Exception as e:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
