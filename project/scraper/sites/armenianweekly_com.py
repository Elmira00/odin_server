import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_armenianweekly_com
import pytz
from dateutil import parser
import re
from datetime import datetime
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://armenianweekly.com/")
def get_news_links_armenianweekly_com(request):
    sitemap_url = Source.objects.get(link="https://armenianweekly.com/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_content = item.find("content:encoded").text.strip() if item.find("content:encoded") else None
            rss_content = BeautifulSoup(rss_content, "html.parser")
            rss_image = rss_content.find("img")["src"] if rss_content.find("img") and rss_content.find("img").get("src") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:10]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_armenianweekly_com(link)
            
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://armenianweekly.com/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        None
    

def fetch_article_details_armenianweekly_com(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers, timeout=10)
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

        #content     
        article_id = soup.find('article',id = 'the-post')
        if article_id:
            article_text_div = article_id.find('div', class_='entry-content entry clearfix')
            if article_text_div:
                for div in article_text_div.find_all('div',class_ = "ts-fab-wrapper ts-fab-icons-text"):
                    div.decompose() 
                    
                for div in article_text_div.find_all('div',id = "inline-related-post"):
                    div.decompose()

                for image in article_text_div.find_all('img'):
                    src = None
                    if image.has_attr('nitro-lazy-src'):
                        src = image['nitro-lazy-src'].strip()
                    elif image.has_attr('data-src'):
                        src = image['data-src'].strip()
                    elif image.has_attr('src') and not image['src'].startswith('data:image'):
                        src = image['src'].strip()
                    
                    if src:
                        gallery_images.append(src)

                    image.decompose() 
                            
                clean_soup_tags(soup, article_text_div)
                content = clean_donya_e_eqtesad_com(article_text_div.prettify())
                content = clean_html_withregex(content)
                
            else:
                div_offset = soup.find('div', class_='entry-content entry clearfix nitro-offscreen')
                if div_offset:
                    
                    for div in div_offset.find_all('div',class_ = "ts-fab-wrapper ts-fab-icons-text"):
                        div.decompose() 
                        
                    for div in div_offset.find_all('div',id = "inline-related-post"):
                        div.decompose()
                        
                    for figure in div_offset.find_all('figure',class_ = "wp-caption alignright"):
                        figure.decompose()
                        
                    for image in div_offset.find_all('img'):
                        src = None
                        if image.has_attr('nitro-lazy-src'):
                            src = image['nitro-lazy-src'].strip()
                        # data-src varsa onu al
                        elif image.has_attr('data-src'):
                            src = image['data-src'].strip()
                        # src varsa ve nitro değilse onu al
                        elif image.has_attr('src') and not image['src'].startswith('data:image'):
                            src = image['src'].strip()
                        
                        if src:
                            gallery_images.append(src)

                        image.decompose() 
                                
                    clean_soup_tags(soup, div_offset)
                    content = clean_donya_e_eqtesad_com(div_offset.prettify())
                    content = clean_html_withregex(content)
                    
                else:
                    content = None
        else:
            content = None

        image_url = scrape_meta_url(soup)

        meta_tag_time = soup.find("meta", {"property": "article:published_time"})
        if meta_tag_time:
            date_str = meta_tag_time["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
            
        else:
            news_shared_date = None
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
