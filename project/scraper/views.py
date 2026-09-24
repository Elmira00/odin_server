from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .models import NewsArticle,ChangedNewsArticle,Source
from django.shortcuts import render
from datetime import datetime,timedelta
from dateutil import parser, tz
import re
from utils.clean_content import extract_relevant_content,clean_haberler,clean_lent,clean_metbuat,clean_trend,\
    clean_milli,clean_anlatilaninotesi,clean_dwcom,clean_ulusal,clean_voaturkce,clean_bianet,clean_birgun,clean_agos,clean_gercekgundem,clean_sabah,clean_samanyoluhaber,\
        clean_cumhuriyet,clean_sozcu,clean_rasthaber,clean_yeniakit,clean_yenisafak,clean_milliyet,clean_aa
from zoneinfo import ZoneInfo
import pytz
import json 




def get_news_links_azertag(request):
    sitemap_url = "https://azertag.az/rss"
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]

        for link in links[:50]:
            title, content, image_url, news_shared_date = fetch_article_details_azertag(link)
        
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()
                
                if existing_article:
                    previous_data = {
                        "title": existing_article.title,
                        "content": existing_article.content,
                    }

                    existing_article.title = title
                    existing_article.content = content
                    existing_article.news_shared_date = news_shared_date
                    existing_article.image_url = image_url
                    existing_article.save()

                    if previous_data["title"] != title or previous_data["content"] != content:
                        ChangedNewsArticle.objects.create(
                            newsarticle=existing_article,
                            title=previous_data["title"] if previous_data["title"] != title else None,  
                            content=previous_data["content"] if previous_data["content"] != content else None,  
                        )

                else:
                    source_instance = Source.objects.get(name="azertag.az")
                    NewsArticle.objects.create(
                        source=source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                    )

    else:
        return None
    
    
def fetch_article_details_azertag(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers)
    
    response.encoding = 'utf-8'  
    
   
    title = None
    content = None
    image_url = None
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        
        title_element = soup.find('div', class_='entry-content p-4')
        if title_element:
            title = title_element.find('h2', class_='entry-title')
            title = title.get_text(strip=True) if title else None
        else:
            title = None
            

        
        content_element = soup.find('div', class_='entry-content p-4')
        if content_element:
            news_body = content_element.find('div', class_='news-body')
            if news_body:
            # content = content_inner.prettify()
                
                for script_tag in news_body.find_all('script'):
                
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                    
                    
                
                content = extract_relevant_content(news_body)
                    
            else:
                content = None
        else:
            content = None
        
        
        image_div = soup.find('div', class_=['entry-content p-4'])
        if image_div:
            print(image_div)
            
            news_body_div = image_div.find('div', class_='news-body')
            if news_body_div:
                                
                image_tag = news_body_div.find('img', class_='news-img')
                if image_tag:
                    base_image_url = image_tag['src']
                    
                    
                    if base_image_url.startswith('/'):
                        image_url = f'https://azertag.az{base_image_url}'
                    else:
                        image_url = base_image_url
                else:
                    image_url = None
            else:
                image_url = None
        else:
            image_url = None
        
            
            
        date_element = soup.find('div', class_ = 'entry-meta')
        if date_element:
            ul_class = date_element.find('ul', class_ = 'global-list')
            
            if ul_class:
                li_class = ul_class.find_all('li')
                first_li = li_class[0]
                date_str = first_li.get_text(strip=True)
                
                try:
                    date_str = date_str.replace('[', '').replace(']', '')
                    
                    date_part, time_part = date_str.split()
                    
                    formatted_date_str = f"{date_part} {time_part}"
                    
                    news_shared_date = parser.parse(formatted_date_str, dayfirst=True) 
                except (ValueError, IndexError) as e:
                    news_shared_date = None
                
                
        else:
            news_shared_date = None

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None
        
        
        # image_div = soup.find('div', class_=['entry-content', 'p-4'])
        # if image_div:
            
        #     news_body_div = image_div.find('div', class_='news-body')
        #     if news_body_div:
                
        #         image_tag = news_body_div.find('img', class_='news-img')
        #         if image_tag and image_tag.get('src'):
        #             base_image_url = image_tag['src']
                    
                    
        #             if base_image_url.startswith('/'):
        #                 image_url = f'https://azertag.az{base_image_url}'
        #             else:
        #                 image_url = base_image_url
        #         else:
        #             image_url = 'No Image Found'
        #     else:
        #         image_url = 'No News body div found'
        # else:
        #     image_url = 'No Image div found'
        
           

#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------

#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------


#---------------------------------FOREIGN WEBSITES------------------------------------------------






# def get_news_links_haberturk(request):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

#     sitemap_url = "https://www.haberturk.com/rss"
#     response = requests.get(sitemap_url,headers=headers)
    
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'xml')
        
        
#         items = soup.find_all('item')
        
#         links = [item.find('link').text for item in items if item.find('link')]
        
#         for link in links[:3]:
#             if not link.startswith("https://www.haberturk.com/"):
#                 continue
            
#             title, content,image_url, news_shared_date = fetch_article_details_haberturk(link)
            
#             if title and content:
#                 existing_article = NewsArticle.objects.filter(url=link).first()
                
#                 if existing_article:
#                     if (existing_article.title != title or 
#                         existing_article.content != content):
                        
#                         if not ChangedNewsArticle.objects.filter(url=link).exists():
#                             ChangedNewsArticle.objects.create(
#                                 newsarticle=existing_article,
#                                 title=existing_article.title,
#                                 content=existing_article.content,
#                                 url=link,  
#                             )
#                         else:
#                             print(f"URL already exists: {link}")
                        
                        
#                         existing_article.title = title
#                         existing_article.content = content
#                         existing_article.save()
#                 else:
#                     source_instance = Source.objects.get(name="haberturk.com")
#                     NewsArticle.objects.create(
#                         source = source_instance,
#                         url=link,
#                         title=title,
#                         content=content,
#                         image_url=image_url,
                        
#                         news_shared_date=news_shared_date
#                     )
#     else:
#         return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)
    
    
    
# def fetch_article_details_haberturk(url):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

#     response = requests.get(url,headers=headers)
#     response.encoding = 'utf-8'  
    
#     title = 'No Title Found'
#     content = 'No Content Found'
#     image_url = 'No Image Found'
#     news_shared_date = None
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         content = soup.prettify()
        
#         print(content)
        
        
        
#         div_class = soup.find('div', class_='featured')
#         if div_class:
#             inner_div = div_class.find('div',class_='pl-5 aspect-h-1')
#             print(inner_div, title)
#             if inner_div:
#                 title = inner_div.find('h1',class_='text-3xl font-black mb-4')
#                 title = title.get_text(strip=True) if title else 'No Title Found'
#             else:
#                 title = 'No inner_div Found'
#         else:
#             title = 'No Title Found'

        
#         div_class = soup.find('div', class_='wrapper px-5 overflow-hidden ')
#         if div_class:
#             article_div_class = div_class.find('div', class_='cms-container')
#             if article_div_class:
#                 # content = content_inner.prettify()
#                 for script_tag in article_div_class.find_all('script'):
            
#                     noscript_tag = soup.new_tag('noscript')
#                     noscript_tag.string = script_tag.string if script_tag.string else ""
#                     script_tag.replace_with(noscript_tag)
                
#                 content = extract_relevant_content(article_div_class)
#             else:
#                 content = 'No Content Inner Found'
#         else:
#             content = 'No Content Element Found'
        
        
        
#         div_class = soup.find('div', class_='wrapper px-5 overflow-hidden ')
#         if div_class:
#             article_div_class = div_class.find('div', class_='cms-container')
#             if article_div_class:
#                 inner_div = article_div_class.find('div', class_='widget-image relative mb-1 block aspect-w-1 aspect-h-1 bg-gray-200 dark:bg-gray-700')
#                 if inner_div:
#                     image = inner_div.find('img')
#                     image_url = image['src'] if image else 'No Image Found'
                    
#                 else:
#                     image_url = 'No inner_div Found'
#             else:
#                 image_url = 'No image_div Found'
#         else:
#             image_url = 'No div_class Found'

            
            
#         month_mapper = {
#             'Ocak': 'January',
#             'Şubat': 'February',
#             'Mart': 'March',
#             'Nisan': 'April',
#             'Mayıs': 'May',
#             'Haziran': 'June',
#             'Temmuz': 'July',
#             'Ağustos': 'August',
#             'Eylül': 'September',
#             'Ekim': 'October',
#             'Kasım': 'November',
#             'Aralık': 'December'
#         }

#         div_class = soup.find('div', class_='featured')

#         if div_class:
#             inner_div = div_class.find('div', class_='relative flex justify-between items-center mb-5 py-3 border-t border-b border-dashed dark:border-gray-800')
#             if inner_div:
#                 flex_div = inner_div.find('div', class_='flex mr-5')
                
#                 if flex_div:
#                     inner_flex_div = flex_div.find('div', class_='h-10 flex flex-col justify-center text-xs')
                    
#                     # if inner_flex_div:
#                     #     spans = inner_flex_div.find_all('span')
#                     #     if spans:
#                     #         span = spans[0]
#                     #         if span:
#                     #         full_text = inner_div.get_text().split('/')[-1].strip()

#                     #         for tr_month, en_month in month_mapper.items():
#                     #             if tr_month in full_text:
#                     #                 full_text = full_text.replace(tr_month, en_month)
#                     #                 break
#                             # if yayin_divs:
#                             #     yayin_tarihi = yayin_divs[0].get_text().replace("Yayınlanma: ", "").strip()

#             #     if yayin_tarihi:
#             #         try:
#             #             news_shared_date = datetime.strptime(yayin_tarihi, "%d.%m.%Y - %H:%M")
#             #         except ValueError as e:
#             #             print(f"Tarih formatı hatası: {e}")
#             #             news_shared_date = None
#             #     else:
#             #         news_shared_date = None
#             # else:
#             #     news_shared_date = None

#             #     try:
#             #         news_shared_date = datetime.strptime(full_text, "%d %B %Y %H:%M")
#             #     except ValueError as e:
#             #         news_shared_date = None
#             else:
#                 news_shared_date = None
#         else:
#             news_shared_date = None

            

#         return title, content,image_url, news_shared_date
#     else:
#         return None, None ,None ,None
    





def get_news_links_trthaber(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = "https://www.trthaber.com/sondakika.rss"
    response = requests.get(sitemap_url,headers=headers)
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        for link in links[:50]:
            title, content, image_url, news_shared_date = fetch_article_details_trthaber(link)
            
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()
                
                if existing_article:
                    if (existing_article.title != title or 
                        existing_article.content != content):
                        
                        if not ChangedNewsArticle.objects.filter(url=link).exists():
                            ChangedNewsArticle.objects.create(
                                newsarticle=existing_article,
                                title=existing_article.title,
                                content=existing_article.content,
                                url=link,  
                            )
                        else:
                            print(f"URL already exists: {link}")
                        
                        
                        existing_article.title = title
                        existing_article.content = content
                        existing_article.save()
                else:
                    source_instance = Source.objects.get(name="trthaber.com")
                    NewsArticle.objects.get_or_create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                    )
    else:
        return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)
    
    
    
def fetch_article_details_trthaber(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    
    title = 'No Title Found'
    content = 'No Content Found'
    image_url = 'No Image Found'
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_element = soup.find('div', class_='news-content-container')
        if title_element:
            title = title_element.find('h1',class_='news-title')
            title = title.get_text(strip=True) if title else 'No Title Found'
        else:
            title = 'No Title Found'

        
        content_element = soup.find('div', class_='news-content-container')
        if content_element:
            content_inner = content_element.find('div', class_='news-content')
            if content_inner:
                # content = content_inner.prettify()
                
                for script_tag in content_inner.find_all('script'):
            
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                
                content = extract_relevant_content(content_inner)
            else:
                content = 'No Content Inner Found'
        else:
            content = 'No Content Element Found'
        
        
        image_element = soup.find('div', class_='news-content-container')
        if image_element:
            image_div = image_element.find('div', class_='news-image')
            if image_div:
                # <picture> içindeki tüm <source> etiketlerini al
                sources = image_div.find_all('source')
                
                # En yüksek çözünürlüğe sahip 'srcset' değerini seçmek
                highest_resolution_url = None
                highest_resolution_width = 0
                
                for source in sources:
                    srcset = source.get('srcset')
                    if srcset:
                        parts = srcset.split(",")
                        for part in parts:
                            url, resolution = part.strip().split(" ")
                            width = int(resolution.replace("w", ""))
                            if width > highest_resolution_width:
                                highest_resolution_width = width
                                highest_resolution_url = url
                
                if highest_resolution_url:
                    image_url = highest_resolution_url
                else:
                    image = image_div.find('picture').find('img')
                    image_url = image['data-src'] if image and 'data-src' in image.attrs else image['src']
            else:
                image_url = 'No Image Div Found'
        else:
            image_url = 'No Image Found'

            
            
        date_div = soup.find('div', class_='source-date-container')
        if date_div:
            span_class = date_div.find('span', class_='created-date')

            if span_class:
                date_str = span_class.get_text(strip=True)

                date_str = date_str.replace('HABER GİRİŞ', '').strip()

                date_time_str = date_str.split(',')[0].strip()

                try:
                    dt = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")
                    
                    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    news_shared_date = formatted_datetime
                except ValueError:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None
    
    
    

    
    
    
def get_news_links_internethaber(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = "https://www.internethaber.com/rss"
    response = requests.get(sitemap_url,headers=headers)
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        for link in links[:50]:
            title, content, image_url, news_shared_date = fetch_article_details_internethaber(link)
            
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()
                
                if existing_article:
                    if (existing_article.title != title or 
                        existing_article.content != content):
                        
                        if not ChangedNewsArticle.objects.filter(url=link).exists():
                            ChangedNewsArticle.objects.create(
                                newsarticle=existing_article,
                                title=existing_article.title,
                                content=existing_article.content,
                                url=link,  
                            )
                        else:
                            print(f"URL already exists: {link}")
                        
                        
                        existing_article.title = title
                        existing_article.content = content
                        existing_article.save()
                else:
                    source_instance = Source.objects.get(name="internethaber.com")
                    NewsArticle.objects.create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                    )
    else:
        return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)
    
    
    
def fetch_article_details_internethaber(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    
    title = 'No Title Found'
    content = 'No Content Found'
    image_url = 'No Image Found'
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_element = soup.find('div', class_='news-detail-top')
        if title_element:
            title = title_element.find('h1',class_='news-detail__title')
            title = title.get_text(strip=True) if title else 'No Title Found'
        else:
            title = 'No Title Found'

        
        content_element = soup.find('div', class_='news-detail-content')
        if content_element:
            content_inner = content_element.find('div', class_='content-text')
            if content_inner:
                # content = content_inner.prettify()
                
                for script_tag in content_inner.find_all('script'):
            
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                
                content = extract_relevant_content(content_inner)
            else:
                content = 'No Content Inner Found'
        else:
            content = 'No Content Element Found'
        
        
        div_class = soup.find('div', class_='news-detail-featured-img img mb-sm')
        if div_class:
            a_tag = div_class.find('a')
            if a_tag:
                picture_tag = a_tag.find('picture')
                if picture_tag:
                    image = picture_tag.find('img')
                    image_url = image['src'] if image else 'No Image Found'
                else:
                    image_url = 'No Picture tag Found'
            else:
                image_url = 'No a_tag Found'
        else:
            image_url = 'Div class Found'

            
            
        date_div = soup.find('div', class_='d-lg-flex align-items-center')
        if date_div:
            inner_div = date_div.find('div', class_='ml-auto')

            if inner_div:
                time_tag = inner_div.find('time')
                if time_tag and 'datetime' in time_tag.attrs:
                    datetime_str = time_tag['datetime']  
                    
                    try:
                        dt = datetime.fromisoformat(datetime_str)
                        
                        formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                        
                        news_shared_date = formatted_datetime
                    except ValueError:
                        news_shared_date = None
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None
    








def get_news_links_bbc(request):
    sitemap_url = "https://www.bbc.com/sitemaps/https-sitemap-com-news-1.xml"

    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url,headers=headers)
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        url_tags = soup.find_all('url')
        
        filtered_links = []
        
        for url_tag in url_tags:
            loc_tag = url_tag.find('loc')
            news_name_tag = url_tag.find('news:name')
            news_language_tag = url_tag.find('news:language')
            news_date_tag = url_tag.find('news:publication_date')

            if loc_tag and news_name_tag and news_language_tag and news_date_tag:
                loc = loc_tag.text
                news_name = news_name_tag.text
                news_language = news_language_tag.text
                news_shared_date = datetime.strptime(news_date_tag.text, "%Y-%m-%dT%H:%M:%SZ")
                
                if loc.startswith("https://www.bbc.com/news/articles/") and news_name == "BBC News" and news_language == "en":
                    filtered_links.append((loc, news_shared_date))

        for link, news_shared_date in filtered_links[:50]:
            title, content, image_url = fetch_article_details_bbc(link)
            
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()
                
                if existing_article:
                    if (existing_article.title != title or 
                        existing_article.content != content):
                        
                        if not ChangedNewsArticle.objects.filter(url=link).exists():
                            ChangedNewsArticle.objects.create(
                                newsarticle=existing_article,
                                title=existing_article.title,
                                content=existing_article.content,
                                url=link,  
                            )
                        else:
                            print(f"URL already exists: {link}")
                        
                        existing_article.title = title
                        existing_article.content = content
                        existing_article.news_shared_date = news_shared_date
                        existing_article.save()
                else:
                    source_instance = Source.objects.get(name = "bbc.com")
                    NewsArticle.objects.create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                    )

    else:
        return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)
    
    
    
def fetch_article_details_bbc(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  
    
    title = 'No Title Found'
    content = 'No Content Found'
    image_url = 'No Image Found'
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        
        article_element = soup.find('article')
        if article_element:
            div_element = article_element.find('div', class_='sc-18fde0d6-0 eeiVGB')
            if div_element:
                title = div_element.find('h1', class_='sc-518485e5-0 bWszMR')
                title = title.get_text(strip=True) if title else 'No Title Found'
        else:
            title = 'No Title Found'

        
        content_element = soup.find('article')
        if content_element:
            
                
            for script_tag in content_element.find_all('script'):
                noscript_tag = soup.new_tag('noscript')
                noscript_tag.string = script_tag.string if script_tag.string else ""
                script_tag.replace_with(noscript_tag)
                
            # content = content_element.prettify()
            content = extract_relevant_content(content_element)

            
        else:
            content = 'No Content Found'
        
        div_class_app = soup.find('div', class_='app')
        if div_class_app:
            article = div_class_app.find('article')
            if article:
                figure = article.find('figure')
                if figure:
                    image_div = soup.find('div', class_='sc-18fde0d6-0 ejjhCR')
                    if image_div:
                        div_class_inner = image_div.find('div',class_ = 'sc-a34861b-1 jxzoZC')
                        if div_class_inner:
                            image = div_class_inner.find('img')
                            image_url = image['srcset'] if image else 'No Image Found'
                        else:
                            image_url = 'No Image Div Inner Found'
                    else:
                        image_url = 'No Image Div Found'
                else:
                    image_url = 'No Figure Found'
            else:
                image_url = 'No Article Found'
        else:
            image_url = 'No Div Class App Found'

            

        return title, content, image_url
    else:
        return None, None, None





def get_news_links_sputnikarm(request):
    sitemap_url = "https://am.sputniknews.ru/sitemap_article.xml?date_start=20240901&date_end=20240917"
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        loc_tags = soup.find_all('loc')
        
        links = [tag.text for tag in loc_tags]


        for link in links[:50]:
            title, content, image_url, news_shared_date = fetch_article_details_sputnikarm(link)
            
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()
                
                if existing_article:
                    if (existing_article.title != title or 
                        existing_article.content != content):
                        
                        if not ChangedNewsArticle.objects.filter(url=link).exists():
                            ChangedNewsArticle.objects.create(
                                newsarticle=existing_article,
                                title=existing_article.title,
                                content=existing_article.content,
                                url=link,  
                            )
                        else:
                            print(f"URL already exists: {link}")
                        
                        
                        existing_article.title = title
                        existing_article.content = content
                        existing_article.save()
                else:
                    source_instance = Source.objects.get(name = 'am.sputniknews.ru')
                    NewsArticle.objects.create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                        
                    )

    else:
        return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)
    
    
    
    
def fetch_article_details_sputnikarm(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  
    
    title = 'No Title Found'
    content = 'No Content Found'
    image_url = 'No Image Found'
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_element = soup.find('div', class_='article__header')
        if title_element:
            title = title_element.find('h1', class_='article__title')
            title = title.get_text(strip=True) if title else 'No Title Found'
        else:
            title = 'No Title Found'

        
            
        div_class = soup.find('div', class_='layout')
        if div_class:
            
            article_element = div_class.find('div', class_='article')
            if article_element:
                
                
                announce_element = article_element.find('div', class_='article__announce-text')
                announce_content = ''
                if announce_element:
                    announce_content = extract_relevant_content(announce_element)
                    
                else:
                    announce_content = 'No Content Found'
                    
                
                content_inner = article_element.find('div', class_='article__body')
                if content_inner:
                    
                    for script_tag in content_inner.find_all('script'):
                        noscript_tag = soup.new_tag('noscript')
                        noscript_tag.string = script_tag.string if script_tag.string else ""
                        script_tag.replace_with(noscript_tag)
                        
                    body_content = extract_relevant_content(content_inner)
                    content = f"{announce_content}\n{body_content}"
                else:
                    content = 'No Content Found'
            else:
                content = 'No Content Found'
        else:
            content = 'No Content Found'
            
        
        
        image_element = soup.find('div', class_='media')
        if image_element:
            image = image_element.find('div', class_='media__size').find('img')
            image_url = image['src'] if image else 'No Image Found'
        else:
            image_url = 'No Image Found'
            
            
        date_class = soup.find('div', class_ = 'article__info')
        if date_class:
            date_class = soup.find('div', class_ = 'article__info-date')
            if date_class:
                date_str = date_class.find('a').text
                try:
                    time_str, date_part = date_str.split()
                        
                    formatted_date = f"{date_part} {time_str}"

                    news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                    
                except (ValueError, IndexError) as e:
                        print(f'Error parsing date: {e}')
                        news_shared_date = None 
            else:
                news_shared_date = None
                
        else:
            news_shared_date = None
            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None


    

    
    

    
def get_news_links_civilge(request):
    sitemap_url = "https://civil.ge/feed"
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        
        links = [item.find('link').text for item in items if item.find('link')]

        for link in links[:20]:
            
            title, content, image_url, news_shared_date = fetch_article_details_civilge(link)
        
            if title and content:
                existing_article = NewsArticle.objects.filter(url=link).first()

                if existing_article:
                    if (existing_article.title != title or 
                        existing_article.content != content):
                        
                        if not ChangedNewsArticle.objects.filter(url=link).exists():
                            ChangedNewsArticle.objects.create(
                                newsarticle=existing_article,
                                title=existing_article.title,
                                content=existing_article.content,
                                url=link,  
                            )
                        else:
                            print(f"URL already exists: {link}")
                        
                        
                        existing_article.title = title
                        existing_article.content = content
                        existing_article.save()
                else:
                    source_instance = Source.objects.get(name = "civil.ge")
                    NewsArticle.objects.create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                    )
                    
            else:
                return HttpResponse("hec bir title ve kontent yoxdur", status=500)

    else:
        return HttpResponse("<h1>Failed to retrieve the page</h1>", status=500)

    
    
   
    
def fetch_article_details_civilge(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    
    title = 'No Title Found'
    content = 'No Content Found'
    image_url = 'No Image Found'
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        div_class  = soup.find('div', class_='main-content tie-col-md-8 tie-col-xs-12')
        if div_class:
            header_element = div_class.find('header', class_='entry-header-outer')
            if header_element:
                div_class = header_element.find('div', class_='entry-header')
                if div_class:
                    title = div_class.find('h1', class_='post-title entry-title')
                    title = title.get_text(strip=True) if title else 'No Title Found'
                else:
                    title = 'No Div class Found'
            else:
                title = 'No Header Element Found'
        else:
            title = 'No Title Found'

        
        div_class  = soup.find('div', class_='main-content tie-col-md-8 tie-col-xs-12')
        if div_class:
            news_content = div_class.find('div', class_='entry-content entry clearfix')
            if news_content:
                    
                for script_tag in news_content.find_all('script'):
                    
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                        
                content = extract_relevant_content(news_content)
                        
            else:
                content = 'entry-content entry clearfix'
        else:
            content = 'No Content Found'
        
            
        
        
        
        div_class_featured = soup.find('div',class_="featured-area")
        if div_class_featured:
            div_class_featured_inner = div_class_featured.find('div',class_="featured-area-inner")
            if div_class_featured_inner:
                figure_class = div_class_featured_inner.find('figure',class_="single-featured-image")
                if figure_class:
                    image = figure_class.find('img')
                    image_url = image['src'] if image else 'No Image Found'
                else:
                    image_url = 'No figure Found'
            else:
                image_url = 'div_class_featured_inner'
        else:
            image_url = 'div_class_featured'
            
        
        div_class  = soup.find('div', class_='main-content tie-col-md-8 tie-col-xs-12')
        if div_class:
            header_class = div_class.find('header', class_='entry-header-outer')
            if header_class:
                div_class = header_class.find('div', class_='entry-header')
                if div_class:
                    date_class_entry = div_class.find('span', class_='date meta-item tie-icon')
                    if date_class_entry:
                        date_str = date_class_entry.text.strip()

                        try:
                            date_part, time_str = date_str.split(' - ')
                            date_part = date_part.replace('/', '.')
                            formatted_date = f"{date_part} {time_str}"
                            news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                            print(news_shared_date)  
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing date: {e}")
                            news_shared_date = None
                    else:
                        news_shared_date = None
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None
    
    
    
    



