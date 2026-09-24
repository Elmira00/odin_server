import json

import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://lenta.ru/")
def get_news_links_lentaru(request):
    sitemap_url = Source.objects.get(link="https://lenta.ru/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        links = []
        link_set = set()
        
        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_lentaru(link)
            if not image_url:
                image_url = rss_image
        
            process_article_data(
                source_link="https://lenta.ru/",
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


def fetch_article_details_lentaru(url):
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
        
        title_element = soup.find('div', class_='topic-body _news')
        if title_element:
            h1_class = title_element.find('h1', class_='topic-body__titles')
            if h1_class:
                span_text = h1_class.find('span', class_='topic-body__title')
                if span_text:
                    title = span_text.get_text(strip=True)  
                else:
                    title = None
            else:
                title = None
        else:
            title = None
            
        # description
        div_yandex_class = soup.find('div', class_='topic-body__title-yandex')
        if div_yandex_class:
            description = div_yandex_class.get_text(strip=True)
        else:
            description = scrape_meta_description(soup)
        if not description:
            description = soup.find("meta", {"name": "og:description"})["content"] if soup.find("meta", {"name": "og:description"}) else None
        if not description:
            script_element = soup.find('script', type='application/ld+json')
            if script_element:
                json_data = json.loads(script_element.string)
                description = json_data.get('description')
            else:
                description = None
            
        content_element = soup.find('div', class_='topic-body _news')
        if content_element:
            news_content = content_element.find('div', class_='topic-body__content')
            if news_content:
                
                gallery_images = extract_gallery_images(news_content)
                clean_soup_tags(soup, news_content)
                content = clean_donya_e_eqtesad_com(news_content.prettify())
                content = clean_html_withregex(content) 
            else:
                content = None
        else: 
            content = None
        
        image_element = soup.find('div', class_='topic-body__title-image')
        if image_element:
            figure_class = image_element.find('figure', class_='picture')
            if figure_class:
                div_class = figure_class.find('div', class_='picture__image-wrap')
                if div_class:
                    a_class = div_class.find('a')
                    if a_class:
                        image = a_class.find('img', class_='picture__image')
                        if image:
                            image_url = image['src']
                        else:
                            image_url = None
                    else:
                        image_url = None
                else:
                    image_url = None
            else:
                image_url = None
        else:
            image_url = None

        if not image_url:
            image_url = scrape_meta_url(soup)

        script = soup.find("script", {"type": "application/ld+json"})
        if script:
            data = json.loads(script.string)
            news_shared_date = data.get("datePublished")
            
        if not news_shared_date:
            jeg_meta_date_div = soup.find('div', class_='topic-header__left-box')
            if jeg_meta_date_div:
                a_element = jeg_meta_date_div.find('a',class_ = "topic-header__item topic-header__time")
                if a_element:
                    date_str = a_element.get_text(strip=True)

                    try:
                        month_map = {
                            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5,
                            'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10,
                            'ноября': 11, 'декабря': 12
                        }
                        time_str, date_str = date_str.split(", ")
                        day, month_name, year = date_str.split(" ")
                        month = month_map.get(month_name.lower())

                        if month:
                            formatted_date = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time_str}"
                            news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                        else:
                            news_shared_date = None
                    except (ValueError, IndexError) as e:
                        news_shared_date = None
                else:
                    news_shared_date = None 
            else:
                news_shared_date = None 

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
    