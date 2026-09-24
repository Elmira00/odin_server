
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime,timedelta
from dateutil import parser

from utils.clean_content import extract_relevant_content,clean_oxu




def get_news_links_oxu(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = "https://oxu.az/sitemap-posts-0.xml"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        loc_tags = soup.find_all('loc')
        
        links = [tag.text for tag in loc_tags]


        for link in links[:50]:
            title, content, image_url, news_shared_date = fetch_article_details_oxu(link)
            
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
                    source_instance = Source.objects.get(name="oxu.az")
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
    
    
def fetch_article_details_oxu(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    
    title = None
    content = None
    image_url = None
    news_shared_date = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        
        title_element = soup.find('div', class_='post-detail-title')
        if title_element:
            title = title_element.find('h1')
            title = title.get_text(strip=True) if title else None
        else:
            title = None

        
        content_element = soup.find('div', class_='post-detail-content')
        if content_element:
            content_inner = content_element.find('div', class_='post-detail-content-inner resize-area')
            if content_inner:
                
                for script_tag in content_inner.find_all('script'):
            
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                
                
                clean_content_first = extract_relevant_content(content_inner)
                content = clean_oxu(clean_content_first)
            else:
                content = None
        else:
            content = None
        
        
        image_element = soup.find('div', class_='post-detail-header')
        if image_element:
            image = image_element.find('div', class_='post-detail-img').find('img')
            image_url = image['src'] if image else None
        else:
            image_url = None
            
            
        meta_div = soup.find('div', class_='post-detail-meta')
        if meta_div:
            date_span = meta_div.find('span')
            if date_span:
                date_text = date_span.get_text(strip=True)

                if "Bu gün" in date_text or "Сегодня" in date_text or "Bugün" in date_text:  # Bugün ucun
                    time_part = date_text.split('/')[1].strip()
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    iso_date = f"{current_date}T{time_part}:00"
                    try:
                        news_shared_date = parser.isoparse(iso_date)
                    except ValueError:
                        news_shared_date = None
                
                elif "Dünən" in date_text or "Вчера" in date_text or "Dün" in date_text:  # Dün ucun
                    time_part = date_text.split('/')[1].strip()
                    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                    iso_date = f"{yesterday_date}T{time_part}:00"
                    try:
                        news_shared_date = parser.isoparse(iso_date)
                    except ValueError:
                        news_shared_date = None
                
                else:  
                    try:
                        raw_date = date_text.split('/')[0].strip()
                        news_shared_date = parser.parse(raw_date, fuzzy=True)
                    except ValueError:
                        news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None
            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None