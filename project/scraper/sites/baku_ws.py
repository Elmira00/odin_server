
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import extract_relevant_content


def get_news_links_bakuws(request):
    sitemap_url = "https://baku.ws/rss"
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]

        for link in links[:55]:
            title, content, image_url, news_shared_date = fetch_article_details_bakuws(link)
            
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
                    source_instance = Source.objects.get(name="baku.ws")
                    NewsArticle.objects.create(
                        source = source_instance,
                        url=link,
                        title=title,
                        content=content,
                        news_shared_date=news_shared_date,
                        image_url=image_url
                        
                    )

    else:
        return None
    
    
def fetch_article_details_bakuws(url):
    response = requests.get(url)
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

        
        content_element = soup.find('div', class_='post-detail')
        if content_element:
            content_inner = content_element.find('div', class_='post-detail-content resize-area')
            if content_inner:
                
                for script_tag in content_inner.find_all('script'):
            
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)
                
                
                # content = content_inner.prettify()
                content = extract_relevant_content(content_inner)

            else:
                content = None
        else:
            content = None
        
        
        image_element = soup.find('div', class_='post-detail-top')
        if image_element:
            image = image_element.find('div', class_='post-detail-img').find('img')
            image_url = image['src'] if image else None
        else:
            image_url = None
            
            
        date_div = soup.find('div', class_='post-date')
        if date_div:
            date_span = date_div.find('span', class_='post-date-inner')
            
            if date_span:
                
                day_span = date_span.find('span', class_='post-date-day')
                month_span = date_span.find('span', class_='post-date-month')
                
                if day_span:
                    day = day_span.get_text(strip=True)
                
                if month_span:
                    month = month_span.get_text(strip=True)
            
            
            year_span = date_div.find('span', class_='post-date-year')
            time_span = date_div.find('span', class_='post-date-time')
            
            if year_span:
                year = year_span.get_text(strip=True)
            
            if time_span:
                time_str = time_span.get_text(strip=True)
            
            try:
                month_map = {
                    'yan': 1, 'fev': 2, 'mar': 3, 'apr': 4, 'may': 5,
                    'iyn': 6, 'iyl': 7, 'avq': 8, 'sen': 9, 'okt': 10,
                    'noy': 11, 'dek': 12
                }
                
                
                month_name = month.lower()
                month_number = month_map.get(month_name, 0)
                
                if month_number:
                    
                    formatted_date = f"{day.zfill(2)}.{str(month_number).zfill(2)}.{year} {time_str}"
                    news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')
                else:
                    news_shared_date = None
            except Exception as e:
                print(f"Error parsing date: {e}")
                news_shared_date = None
        else:
            news_shared_date = None

            

        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None