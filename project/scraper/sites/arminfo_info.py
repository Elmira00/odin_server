import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images

from utils.decorators import check_source_active


@check_source_active("https://arminfo.info/")
def get_news_links_arminfo_info(request):
    sitemap_url = Source.objects.get(link="https://arminfo.info/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        links = [item.find('link').text for item in items if item.find('link')]
        
        for link in links[:5]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_arminfo_info(link)
            
            process_article_data(
                source_link="https://arminfo.info/",
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

        
def fetch_article_details_arminfo_info(url):
    try:
        headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
        response = requests.get(url,headers=headers, timeout=10)
        response.encoding = 'utf-8'  
    except requests.exceptions.ConnectionError:
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

        article_text_div = soup.find("div", style=lambda s: s and "font-size:14px" in s and "font-family:verdana" in s)
        if article_text_div:
            gallery_images = extract_gallery_images(article_text_div)

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content) 
        else:
            content = None
            
        image_url = scrape_meta_url(soup)

        date_wrapper_div = soup.find('div', class_='intrig_style')

        if date_wrapper_div:
            all_divs = date_wrapper_div.find_all('div')
            if all_divs:
                first_div = all_divs[0]
                if first_div:
                    date_str = first_div.get_text(strip=True).replace('\xa0', ' ')

                    month_map = {
                        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5,
                        'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10,
                        'ноября': 11, 'декабря': 12
                    }

                    try:
                        cleaned = date_str.split(',')[-1].strip()  
                        parts = cleaned.split()

                        day = parts[0]
                        month_name = parts[1].lower()
                        year = parts[2]
                        time_str = parts[3]

                        month = month_map.get(month_name)

                        if month:
                            formatted_date = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time_str}"
                            news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                        else:
                            news_shared_date = None

                    except (IndexError, ValueError) as e:
                        news_shared_date = None

                else:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

        return title, description, content, image_url,gallery_images, news_shared_date
    
    else:
        return None, None, None, None, None, None
