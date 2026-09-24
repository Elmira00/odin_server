
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://report.az/")
def get_news_links_report(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://report.az/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        for link in links[:50]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_report(link)
            
            process_article_data(
            source_link="https://report.az/",
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
    
    
    
def fetch_article_details_report(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

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
            
            
        content_div = soup.find('div', class_='editor-body')
        if content_div:
            
            unwanted_div_classes = [
                'subs-in-social subs-whatsapp',
                'subs-in-social subs-telegram',
                'subs-in-social subs-facebook',
            ]
            for unwanted_class in unwanted_div_classes:
                for div in content_div.find_all('div', class_=unwanted_class):
                    div.decompose()

            gallery_images = extract_gallery_images(content_div)
            clean_soup_tags(soup, content_div)
            content = clean_donya_e_eqtesad_com(content_div.prettify())
            content = clean_html_withregex(content)
            

        else:
            content = None

        image_url = scrape_meta_url(soup)
            
            
        date_div = soup.find('div', class_='news-date')
        
        
        if date_div:
            spans = date_div.find_all('span')
            if len(spans) >= 2:
                date_str = spans[0].get_text(strip=True).replace(',', '').strip()
                time_str = spans[1].get_text(strip=True)

                try:
                    month_map = {
                        'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4, 'may': 5, 'iyun': 6,
                        'iyul': 7, 'avqust': 8, 'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12
                    }


                    date_parts = date_str.split()
                    day = date_parts[0]  # Gün 
                    month_name = date_parts[1].lower()  # Ay adı
                    year = date_parts[2]  # ıl

                    month = month_map.get(month_name, 0)

                    if month:
                        formatted_date = f"{str(int(day)).zfill(2)}.{month}.{year} {time_str}"
                        news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                    else:
                        news_shared_date = None

                except (ValueError, IndexError) as e:
                    print(f'Hata: {e} - Hatalı tarih verisi: {date_str}')
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None


        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    
