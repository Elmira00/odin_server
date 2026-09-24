import requests
from bs4 import BeautifulSoup
from scraper.models import Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.sozcu.com.tr/")
def get_news_links_sozcu(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://www.sozcu.com.tr/").rss_link
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("media:content")["url"] if item.find("media:content") else None
            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_sozcu(link)
            if title == "url not matched":
                continue
            if not image_url:
                image_url = rss_image
            
            process_article_data(
                source_link="https://www.sozcu.com.tr/",
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
    
    
def fetch_article_details_sozcu(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.url != url:
        return "url not matched", None, None ,None,None, None
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
        
        div_class = soup.find('div', class_='article-body')
        if not div_class.get_text(strip=True):
            div_class = soup.find('section', class_='news-gallery')
        article_div_class = div_class
        if article_div_class:
            gallery_images = extract_gallery_images(article_div_class)
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
        else:
            content = None
        
        image_url = scrape_meta_url(soup)
        #updated img scraping
        if not image_url:
            img_div = soup.find('div', class_='main-image')
            if img_div:
                img_tag = img_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag['src']
            
            
        if not news_shared_date:
            header_class = soup.find('header', class_='mb-4')
            if header_class:
                inner_div = header_class.find('div', class_='content-meta-dates mb-4')

                if inner_div:
                    span_class = inner_div.find('span', class_='content-meta-date')
                    
                    time_tag = span_class.find('time')

                    if time_tag and time_tag.has_attr('datetime'):
                        datetime_str = time_tag['datetime']
                        
                        dt = datetime.fromisoformat(datetime_str[:-6])  
                        formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                        
                        news_shared_date = formatted_datetime
                    else:
                        news_shared_date = None
                    
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
            

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    