

import re
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime


from utils.decorators import check_source_active


@check_source_active("https://kaztag.kz/ru/")
def get_news_links_kaztag_kz(request):
    headers =  {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    website_url = "https://kaztag.kz"
    urls = ["https://kaztag.kz/ru/news/","https://kaztag.kz/ru/news/?PAGEN_1=2","https://kaztag.kz/ru/news/?PAGEN_1=3"]


    links = []

    for url in urls:
        response = requests.get(url,headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_list = soup.find_all('div', class_='post type-post double')
            
            if div_list:

                for y_div in div_list:
                    ys_link = y_div.find('div', class_='post-header')
                    if ys_link:
                        h3_class = ys_link.find('h3', class_='post-title')
                        if h3_class:
                            a_tag = ys_link.find('a', href=True)
                            if a_tag and a_tag.has_attr('href'):
                                link = website_url + a_tag['href']
                                if link not in links:
                                    links.append(link)
                                    

                                    
                                    
        for link in links:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_kaztag_kz(link)

            process_article_data(
            source_link="https://kaztag.kz/ru/",
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
    


def fetch_article_details_kaztag_kz(url):
    headers =  {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
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
        

        #Content
        
        article_tag = soup.find('article')
        if article_tag:

            article_div_class = article_tag.find('div', class_='post-content')
            if article_div_class:
                
                # gallery_images = extract_gallery_images(article_div_class)
                
                cdn_prefix = "http://www.irdiplomacy.ir"
                images = article_div_class.find_all('img')

                for image in images:
                    if image and image.has_attr('src'):
                        src = image['src']
                        
                        
                        full_src = cdn_prefix + src

                        gallery_images.append(full_src)

                for image in images:
                    image.decompose()
                
                clean_soup_tags(soup, article_div_class)
                content = clean_donya_e_eqtesad_com(article_div_class.prettify())
                content = clean_html_withregex(content) 
                
                
            else:
                content = None
        else:
            content=None
        
        image_url = scrape_meta_url(soup)

            
        #Time
        
        inner_div = soup.find('div', class_='post-byline')

        if inner_div:
            p_class = inner_div.find('p')
            
            if p_class:
                date_str = p_class.get_text(strip=True)
                
                try:
                    month_map = {
                        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5,
                        'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10,
                        'ноября': 11, 'декабря': 12
                    }

                    date_part, time_str = date_str.split(", ")
                    day, month_name, year = date_part.split(" ")

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


        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
