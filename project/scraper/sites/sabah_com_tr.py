import requests
import re
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.sabah.com.tr/")
def get_news_links_sabah(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = "https://www.sabah.com.tr/rss/dunya.xml"
    response = requests.get(sitemap_url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None
            if link and link not in link_set and rss_image:
                links.append((link, rss_image))
                link_set.add(link)

        for link, rss_image in links:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_sabah(link)
            if image_url is None:
                image_url = rss_image
            
            process_article_data(
                source_link="https://www.sabah.com.tr/",
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
    
    
def fetch_article_details_sabah(url):
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
        description = scrape_meta_description(soup)
        news_shared_date = soup.find("meta", {"name": "datePublished"})["content"] if soup.find("meta", {"name": "datePublished"}) else None
        # possible_classes = [
        #     'detail-text-area',
        #     'newsBox',
        #     'page flex-grow-1',
        #     'topDetail'
        # ]
        # div_class = None

        # for class_name in possible_classes:
        #     div_class = soup.find('div', class_=class_name)
        #     if div_class:
        #         break

        # if div_class:
        #     CLASS_MATCHES = {
        #         "div": ["application-widget", "market-banner"],
        #     }
        #     for tag_name, class_list in CLASS_MATCHES.items():
        #         for class_name in class_list:
        #             for tag in soup.find_all(tag_name, class_=class_name):
        #                 tag.decompose()

        div_class = soup.find("section", class_="post")

        CLASS_MATCHES = {
            "div": ["share", "malker", "credit", "app-widget"],
            "a": ["googlenews-link"]
        }
        for tag_name, class_list in CLASS_MATCHES.items():
            for class_name in class_list:
                for tag in div_class.find_all(tag_name, class_=class_name):
                    tag.decompose()

        for tag in div_class.find_all(["ul", "figure", "iframe", "aside", 'img', 'svg']):
            tag.decompose()

        gallery_images = extract_gallery_images(div_class)
        clean_soup_tags(soup, div_class)
        content = clean_donya_e_eqtesad_com(div_class.prettify())
        content = clean_html_withregex(content)
       

        image_url = scrape_meta_url(soup)
        if not image_url:
            tag = soup.find("figure", class_="newsImage")
            if tag:
                img_tag = tag.find("img")
                if img_tag and img_tag.has_attr("src"):
                    image_url = img_tag["src"]
                    
        #Tariux almaq ucun
        
        # span_class = soup.find('span', class_='textInfo align-center')
        # if span_class:
        #     all_spans = span_class.find_all('span')
        #     if all_spans:
        #         span_publish = all_spans[0]
                
        #         if span_publish:
        #             publish_text = span_publish.get_text(strip=True) 
                    
        #             if publish_text:
        #                 match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})(\d{2}:\d{2})', publish_text)
                        
        #                 if match:
        #                     date_part = match.group(1)  # 14.2.2025
        #                     time_part = match.group(2)  # 09:54
                            
        #                     news_shared_date = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%Y %H:%M")
        #                 else:
        #                     news_shared_date = None
        #         else:
        #             news_shared_date = None
        #     else:
        #         news_shared_date = None

        # else:
        #     month_mapper = {
        #         'Ocak': 'January',
        #         'Şubat': 'February',
        #         'Mart': 'March',
        #         'Nisan': 'April',
        #         'Mayıs': 'May',
        #         'Haziran': 'June',
        #         'Temmuz': 'July',
        #         'Ağustos': 'August',
        #         'Eylül': 'September',
        #         'Ekim': 'October',
        #         'Kasım': 'November',
        #         'Aralık': 'December'
        #     }

        #     div_class = soup.find('div', class_='share')
        #     if div_class:
        #         smal_class = div_class.find('small', class_='post-info')
        #         if smal_class:
        #             span_classes = smal_class.find_all('span')
        #             if span_classes:
        #                 span_publish = span_classes[0]
        #                 if span_publish:
        #                     publish_text = span_publish.get_text(strip=True) 

        #                     try:
        #                         parts = publish_text.split(":", 1)[1].strip().split()

        #                         if len(parts) >= 3:
        #                             day = parts[0]  
        #                             month_tr = parts[1]  
        #                             year = parts[2]  
        #                             time_part = parts[3] if len(parts) > 3 else "00:00"

        #                             if len(time_part) == 2 and time_part.isdigit():
        #                                 time_part += ":00"

        #                             month_en = month_mapper.get(month_tr, month_tr)
        #                             news_shared_date = datetime.strptime(f"{day} {month_en} {year} {time_part}", "%d %B %Y %H:%M")

        #                     except Exception as e:
        #                         print(f"Error parsing date: {e}")
        #                 else:
        #                     news_shared_date = None
        #             else:
        #                 news_shared_date = None
        #         else:
        #             news_shared_date = None
        #     else:
        #         news_shared_date = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
