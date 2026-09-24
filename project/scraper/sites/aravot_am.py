# import requests
# from bs4 import BeautifulSoup
# from scraper.models import NewsArticle,ChangedNewsArticle,Source
# import re
# from datetime import datetime
# from utils.process_article import process_article_data
# from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
# from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags, extract_gallery_images


# from utils.decorators import check_source_active


# @check_source_active("https://www.aravot.am/")
# def get_news_links_aravot_am(request):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
#     sitemap_url = "https://www.aravot.am/newsfeed/"
#     response = requests.get(sitemap_url,headers=headers)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         links = []
#         link_set = set()       
        
#         category_divs = soup.find('div', cass='category_items') 
#         if category_divs:
            
#             div_rows = category_divs.find_all('div', class_='row')
#             if div_rows:
#                 for div_row in div_rows:
#                     col_3_div = div_row.find('div', class_='col-3')
#                     if col_3_div:
#                         a_tag = col_3_div.find('a')
#                         if a_tag and a_tag.has_attr('href'):
#                             link = a_tag['href']
#                             links.append(link)
#                             link_set.add(link)
                            

#         for link in links[:30]:
#             title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_aravot_am(link)
#             process_article_data(
#             source_link="https://www.aravot.am/",
#             link=link,
#             title=title,
#             description=description,
#             content=content,
#             image_url=image_url,
#             gallery_images=gallery_images,
#             news_shared_date=news_shared_date
#         )
    

    
# def fetch_article_details_aravot_am(url):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

#     response = requests.get(url,headers=headers, timeout=5)
#     response.encoding = 'utf-8'  
    
#     title = None
#     description = None
#     content = None
#     gallery_images = []
#     image_url = None
#     news_shared_date = None
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         title = scrape_meta_title(soup)
#         description = scrape_meta_description(soup)

        
        
    
#         article_text_div = soup.find('div', class_='post_content')
#         if article_text_div:
                
#             for script_tag in article_text_div.find_all('script'):
#                 script_tag.decompose()

#             gallery_images = extract_gallery_images(article_text_div)

#             for div in article_text_div.find_all('div', class_='border p-2 text-center rounded-3 mb-3'):
#                 div.decompose()

            
#             clean_soup_tags(soup, article_text_div)
#             content = clean_donya_e_eqtesad_com(article_text_div.prettify())
#             content = clean_html_withregex(content)
#         else:
#             content = None

        
        
#         image_url = scrape_meta_url(soup)


#         date_span = soup.find('span', class_='small')
#         if date_span:
#             full_text = date_span.get_text(separator=" ", strip=True)

#             try:
#                 month_map = {
#                     'Հունվար': 1,
#                     'Փետրվար': 2,
#                     'Մարտ': 3,
#                     'Ապրիլ': 4,
#                     'Մայիս': 5,
#                     'Հունիս': 6,
#                     'Հուլիս': 7,
#                     'Օգոստոս': 8,
#                     'Սեպտեմբեր': 9,
#                     'Հոկտեմբեր': 10,
#                     'Նոյեմբեր': 11,
#                     'Դեկտեմբեր': 12,
#                 }

#                 parts = full_text.split()

#                 if len(parts) >= 2:
#                     month_name = parts[0]
#                     rest = parts[1]  
#                     time = parts[2] if len(parts) > 2 else '00:00'

#                     day, year = rest.replace(',', ' ').split()
#                     month = month_map.get(month_name, 0)

#                     if month:
#                         formatted = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time}"
#                         news_shared_date = datetime.strptime(formatted, '%d.%m.%Y %H:%M')
#                     else:
#                         news_shared_date = None
#                 else:
#                     news_shared_date = None

#             except Exception as e:
#                 news_shared_date = None
#         else:
#             news_shared_date = None
            
            
#         return title,description, content, image_url,gallery_images, news_shared_date
#     else:
#         return None, None, None ,None,None, None

import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
import re
from datetime import datetime
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags, extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://www.aravot.am/")
def get_news_links_aravot_am(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.aravot.am/newsfeed/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        link_set = set()       
        
        category_divs = soup.find('div', class_='category_items') ## 
        if category_divs:
            
            div_rows = category_divs.find_all('div', class_='row')
            if div_rows:
                for div_row in div_rows:
                    col_3_div = div_row.find('div', class_='col-3')
                    if col_3_div:
                        a_tag = col_3_div.find('a')
                        if a_tag and a_tag.has_attr('href'):
                            link = a_tag['href']
                            links.append(link)
                            link_set.add(link)
                            

        for link in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_aravot_am(link)
            process_article_data(
            source_link="https://www.aravot.am/",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date
        )
    

def fetch_article_details_aravot_am(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers, timeout=5)
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

        
        article_text_div = soup.find('div', class_='post_content')
        if article_text_div:
                
            for script_tag in article_text_div.find_all('script'):
                script_tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for div in article_text_div.find_all('div', class_='border p-2 text-center rounded-3 mb-3'):
                div.decompose()

            
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        
        
        image_url = scrape_meta_url(soup)


        # ================= TARİX HİSSƏSİ (YENİLƏNDİ) =================
        # 1. İlk olaraq Meta/Time teqindən hazır ISO formatlı tarixi götürürük
        meta_time = soup.find('meta', property='article:published_time') or soup.find('time')
        if meta_time:
            date_raw = meta_time.get('content') or meta_time.get('datetime')
            if date_raw:
                try:
                    news_shared_date = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
                except Exception:
                    news_shared_date = None

        # 2. Meta teq tapılmazsa, HTML text daxilindən erməni dilində pars edirik
        if not news_shared_date:
            meta_div = soup.find('div', class_='single-meta') or soup.find('span', class_='small')
            if meta_div:
                full_text = meta_div.get_text(separator=" ", strip=True).replace('\xa0', ' ')

                try:
                    month_map = {
                        'Հունվար': 1, 'Հունվարի': 1,
                        'Փետրվար': 2, 'Փետրվարի': 2,
                        'Մարտ': 3, 'Մարտի': 3,
                        'Ապրիլ': 4, 'Ապրիլի': 4,
                        'Մայիս': 5, 'Մայիսի': 5,
                        'Հունիս': 6, 'Հունիսի': 6,
                        'Հուլիս': 7, 'Հուլիսի': 7,
                        'Օգոստոս': 8, 'Օգոստոսի': 8,
                        'Սեպտեմբեր': 9, 'Սեպտեմբերի': 9,
                        'Հոկտեմբեր': 10, 'Հոկտեմբերի': 10,
                        'Նոյեմբեր': 11, 'Նոյեմբերի': 11,
                        'Դեկտեմբեր': 12, 'Դեկտեմբերի': 12,
                    }

                    match = re.search(
                        r"([\u0531-\u058F]+)\s+(\d{1,2})\s*,?\s*(\d{4})\s+(\d{1,2}:\d{2})",
                        full_text,
                    )
                    if match:
                        month_name, day, year, time_str = match.groups()
                        month = month_map.get(month_name)
                        if month:
                            formatted = (
                                f"{day.zfill(2)}.{str(month).zfill(2)}.{year}"
                                f" {time_str}"
                            )
                            news_shared_date = datetime.strptime(
                                formatted, "%d.%m.%Y %H:%M"
                            )
                except Exception:
                    news_shared_date = None
            else:
                news_shared_date = None
        # ==============================================================
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None