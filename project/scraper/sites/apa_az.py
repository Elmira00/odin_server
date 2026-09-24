import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime

from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags, extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://apa.az/")
def get_news_links_apa(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = Source.objects.get(link="https://apa.az/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item') 
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link :
                if link not in link_set:
                    
                    links.append((link))
                    link_set.add(link)
                
        
        
        
        for link in links[:40]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_apa(link)
            
            process_article_data(
            source_link="https://apa.az/",
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

        
        
        
def fetch_article_details_apa(url):
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

        
        content_main = soup.find('div', class_='content_main')
        if content_main:
            article_text_div = content_main.find('div', class_='news_content mt-site')
            if article_text_div:
                
                for div_class in article_text_div.find_all('div', class_='logo'):
                    div_class.decompose()
                    
                    
                for div_tag in article_text_div.find_all('div', class_='tags mt-site'):
                    div_tag.decompose()
                
                
                news_gallery_div = article_text_div.find('div', class_='news_in_gallery')
                if news_gallery_div:
                
                    for image in article_text_div.find_all('img'):
                        final_url = None
                        parent_a = image.find_parent('a')

                        if parent_a and parent_a.has_attr('href'):
                            href = parent_a['href'].strip()
                            if '/resize/' in href:
                                final_url = href

                        if not final_url:
                            if image.has_attr('data-src'):
                                final_url = image['data-src'].strip()
                            elif image.has_attr('src'):
                                final_url = image['src'].strip()

                        if final_url:
                            gallery_images.append(final_url)

                        if parent_a:
                            parent_a.decompose()
                        else:
                            image.decompose()


                
                clean_soup_tags(soup, article_text_div)
                content = clean_donya_e_eqtesad_com(article_text_div.prettify())
                content = clean_html_withregex(content)
            else:
                content = None
        else:
            content = None
        
        
        image_url = scrape_meta_url(soup)
            
              
        content_main = soup.find('div', class_='content_main')
        if content_main:
            date_news_div = content_main.find('div', class_='date_news')
            if date_news_div:
                date_div = date_news_div.find('div', class_='date')
                if date_div:
                    date_span = date_div.find('span', class_='date')
                    if date_span:
                        date_str = date_span.get_text(strip=True)
                        try:
                            month_map = {
                                'yanvar': 1,
                                'fevral': 2,
                                'mart': 3,
                                'aprel': 4,
                                'may': 5,
                                'iyun': 6,
                                'iyul': 7,
                                'avqust': 8,
                                'sentyabr': 9,
                                'oktyabr': 10,
                                'noyabr': 11,
                                'dekabr': 12
                            }

                            
                            date_parts = date_str.split()
                            day = date_parts[0]
                            month = month_map.get(date_parts[1], 0)
                            year = date_parts[2]
                            time = date_parts[3]  

                            if month:
                                formatted_date = f"{day.zfill(2)}.{str(month).zfill(2)}.{year} {time}"
                                news_shared_date = datetime.strptime(formatted_date, '%d.%m.%Y %H:%M')

                        except ValueError:
                            news_shared_date = None
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
