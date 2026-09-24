

import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from urllib.parse import urljoin

from utils.decorators import check_source_active


@check_source_active("https://www.hdp.org.tr/tr/")
def get_news_links_hdp(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.hdp.org.tr/tr/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        base_website_url = "https://www.hdp.org.tr"
        
        
        box_links = soup.find_all('div', class_='box-content-header')
        for box_link in box_links:
            a_class = box_link.find('a')
            if a_class and a_class.has_attr('href'):
                link = a_class['href']
                links.append(base_website_url+link)

        for link in links[:16]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_hdp(link)
            
            process_article_data(
            source_link="https://www.hdp.org.tr/tr/",
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
    
    
def fetch_article_details_hdp(url):
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
        
        
        # content Alma
        page_content_div= soup.find('div', class_='page-content')
        if page_content_div:


            gallery_images = extract_gallery_images(page_content_div)
            clean_soup_tags(soup, page_content_div)
            content = clean_donya_e_eqtesad_com(page_content_div.prettify())
            content = clean_html_withregex(content)
            
            
        else:
            content = None
        
        #image almaq
        
        
        website_url = "https://www.hdp.org.tr"
        image_div = soup.find('div', class_='page-content-img mb-2')
        if image_div:
            img_tag = image_div.find('img')
            if img_tag:
                image_url = website_url+img_tag['src']
            else:
                image_url = None
        else:
            image_url = None


                    

        #date almaq
        month_mapper = {
                'Ocak': 'January',
                'Şubat': 'February',           
                'Mart': 'March',
                'Nisan': 'April',
                'Mayıs': 'May',
                'Haziran': 'June',
                'Temmuz': 'July',
                'Ağustos': 'August',
                'Eylül': 'September',
                'Ekim': 'October',
                'Kasım': 'November',
                'Aralık': 'December'
            }

        div_class = soup.find('div', class_='page-content')
        if div_class:
            inner_div_classes = div_class.find_all('div')
            if inner_div_classes:
                inner_div = inner_div_classes[-1]
                if inner_div:
                    p_tags = div_class.find_all('p')
                    if p_tags:
                        last_p = p_tags[-1]  
                        strong_tag = last_p.find('strong')

                        if strong_tag:
                            publish_text = strong_tag.get_text(strip=True) 
                            
                            try:
                                parts = publish_text.split() 
                                if len(parts) == 3:  
                                    day, month_tr, year = parts  
                                    month_en = month_mapper.get(month_tr, month_tr)  
                                    
                                    news_shared_date = datetime.strptime(f"{day} {month_en} {year} 07:07", "%d %B %Y %H:%M")

                            except Exception as e:
                                print(f"Error parsing date: {e}")
                        else:
                            news_shared_date = None
                    
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None
            

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None

