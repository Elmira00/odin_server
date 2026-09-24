

import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://www.voaturkce.com/")
def get_news_links_voaturkce(request):
    sitemap_url = Source.objects.get(link="https://www.voaturkce.com/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            title = item.find('title').text.strip() if item.find('title') else None
            pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else None

            if link and pub_date and title:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                
                links.append((link, title, dt))
                link_set.add(link)

        for link, title, news_shared_date in links[:20]:
            description, content, image_url,gallery_images = fetch_article_details_voaturkce(link)  
            
            process_article_data(
            source_link="https://www.voaturkce.com/",
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
    
    
def fetch_article_details_voaturkce(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  
    

    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        description_meta = soup.find("meta", attrs={"name": "description"})
        if description_meta and description_meta.get("content"):
            description = description_meta["content"]
        else:
            description = None
        
        # Content Alma
        div_post_container = soup.find('div', class_='content-floated-wrap fb-quotable')
        if div_post_container:
            div_class = div_post_container.find('div', class_='wsw')
            if div_class:
                    
                for media_tag in div_class.find_all('div', class_='media-block also-read'):
                    media_tag.decompose()
                    
                for div_media_pholder in div_class.find_all('div', class_='media-pholder media-pholder--video'):
                    div_media_pholder.decompose()
                    
                gallery_images = extract_gallery_images(div_class)   
                clean_soup_tags(soup, div_class)
                content = clean_donya_e_eqtesad_com(div_class.prettify())
                content = clean_html_withregex(content)
                
        else:
            content = None
        # Image Alma
        
        
        div_class = soup.find('div', class_='img-wrap')

        if div_class:
            image_class = div_class.find('div', class_='thumb thumb16_9')
            
            if image_class:
                image = image_class.find('img')

                if image:
                    image_url = image.get('srcset') or image.get('data-srcset') or image.get('src')
                    if image_url:
                        image_url = image_url.replace('_w250_', '_w1023_') 
                else:
                    image_url = None
            else:
                image_url = None
        else:
            image_url = None
        

        return description, content, image_url,gallery_images
    
    else:
        return None, None, None, None
