import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime,timedelta
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://bianet.org/")
def get_news_links_bianet(request):
    sitemap_url = Source.objects.get(link="https://bianet.org/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
         
        links = []
        link_set = set()
 
        for item in items[:50]:
            link = item.find('link').text.strip() if item.find('link') else None
            pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else None
            description = item.find("description").text.strip() if item.find("description") else None

            if link and pub_date and description:
                if link not in link_set:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")

                    dt_baku = dt + timedelta(hours=1)
                    
                    links.append((link, dt_baku, description))
                    link_set.add(link)
                     
        for link, news_shared_date, description in links:
            title, content, image_url, gallery_images = fetch_article_details_agos(link)
            
            process_article_data(
                source_link="https://bianet.org/",
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
    
    
def fetch_article_details_agos(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
        
        content_div = soup.find('div', class_='content')

        if content_div:
            if content_div.find("a", class_="ccard"):
                content_div.find("a", class_="ccard").decompose()

            gallery_images = extract_gallery_images(content_div)
            gallery_images = [img for img in gallery_images if img.endswith((".jpg", ".jpeg", ".png"))]
            clean_soup_tags(soup, content_div)
            content = clean_donya_e_eqtesad_com(content_div.prettify())
            content = clean_html_withregex(content)
                                
        else:
            content = None 
        
        image_url = scrape_meta_url(soup)

        return title, content, image_url, gallery_images
    
    else:
        return None, None, None, None
