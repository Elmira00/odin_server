import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from django.utils import timezone
from zoneinfo import ZoneInfo

from utils.decorators import check_source_active


@check_source_active("https://formulanews.ge/")
def get_news_links_formulanews_ge(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://formulanews.ge/Category/all"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []                
        base_website_url = "https://formulanews.ge"
            
        main_slider_divs = soup.find_all('div', class_='main__new__slider__desc')
        if main_slider_divs:
            for main_slider_div in main_slider_divs:
                a_tag = main_slider_div.find('a')
                if a_tag and a_tag.has_attr('href'):
                    link = a_tag['href']
                    links.append(base_website_url + link)
                
        for link in links[:15]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_formulanews_ge(link)

            process_article_data(
                source_link="https://formulanews.ge/",
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
    

def fetch_article_details_formulanews_ge(url):
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
        if not description:
            description = soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else None

        #content     

        div_class = soup.find('article', class_='article')
        if div_class:
            article_div_class = div_class.find('section', class_='article-content')
            
            if article_div_class:      
                unwaned_divs = ['news__inner__main__image']
                        
                for unwanted_div in unwaned_divs:
                    for div in article_div_class.find_all('div', class_=unwanted_div):
                        div.decompose()

                gallery_images = extract_gallery_images(article_div_class)
                clean_soup_tags(soup, article_div_class)
                content = clean_donya_e_eqtesad_com(article_div_class.prettify())
                content = clean_html_withregex(content)
            else:
                content = None
        else:
            content = None
        
        image_url = scrape_meta_url(soup)
        
        # Tarix
        date_div = soup.find('div', class_='news__inner__images_created')
        if date_div:
            full_text = date_div.get_text(separator=" ", strip=True) 
            try:
                parts = full_text.split()

                if len(parts) >= 4:
                    day = parts[0]
                    month_txt = parts[1]
                    year = parts[2]
                    time = parts[3]

                    month_map = {
                        'იან': 1,
                        'თებ': 2,
                        'მარ': 3,
                        'აპრ': 4,
                        'მაი': 5,
                        'ივნ': 6,
                        'ივლ': 7,
                        'აგვ': 8,
                        'სექ': 9,
                        'ოქტ': 10,
                        'ნოე': 11,
                        'დეკ': 12,
                    }
                    month = month_map.get(month_txt[:3], 0)

                    if month:
                        formatted = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time}"
                        news_shared_date = datetime.strptime(formatted, '%d.%m.%Y %H:%M')
                        news_shared_date = timezone.make_aware(news_shared_date, timezone=ZoneInfo("Asia/Tbilisi")) 
                    else:
                        news_shared_date = None
                else:
                    news_shared_date = None
            except Exception as e:
                news_shared_date = None
        else:
            news_shared_date = None
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
