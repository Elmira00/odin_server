import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime

from utils.decorators import check_source_active


@check_source_active("https://www.rbc.ua/")
def get_news_links_rbc_ua(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://www.rbc.ua/").rss_link
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        
        links = []
        link_set = set() 
        
        for item in items:
            link = item.find('link').text if item.find('link') else None
            pub_date = item.find('pubDate').text if item.find('pubDate') else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None
            rss_title = item.find('title').text if item.find('title') else None
            rss_description = item.find('description').text if item.find('description') else None
            rss_content = item.find('content:encoded').text if item.find('content:encoded') else None

            if link and pub_date and rss_image and rss_title and rss_description and rss_content:
                if link not in link_set:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z") 
                    
                    links.append((link, dt, rss_image, rss_title, rss_description, rss_content))
                    link_set.add(link)

        for link, news_shared_date, rss_image, rss_title, rss_description, rss_content in links[:15]:
            title,description, content, image_url,gallery_images = fetch_article_details_rbc_ua(link)
            
            if not image_url:
                image_url = rss_image
            if not title:
                title = rss_title
            if not description:
                description = rss_description
            if not content:
                content = rss_content
            
            process_article_data(
                source_link="https://www.rbc.ua/",
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

    
def fetch_article_details_rbc_ua(url):
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

        #content     
        website_url = "https://www.rbc.ua"
        article_text_div = soup.find('div', class_='txt')
        if article_text_div:
            
            unwanted_div_classes = ["news_tags_block", "RBC_VIDEO"]
            for div_class in unwanted_div_classes:
                for div in article_text_div.find_all('div', class_=div_class):
                    div.decompose()

            for div in article_text_div.find_all('div', class_="publication-backlink"):
                if "Вас может заинтересовать" in div.get_text():
                    div.decompose()
                    
            trigger_phrase = "Срочные и важные сообщения о войне России против Украины читайте на канал"
            for p_tag in article_text_div.find_all('p'):
                if trigger_phrase in p_tag.get_text():
                    p_tag.decompose()
                    
            for img in article_text_div.find_all('img'):
                src_value = img.get('data-src')
                if src_value:
                    if not src_value.startswith("http"):
                        src_value = website_url + src_value
                    img.attrs = {'src': src_value}

            gallery_images = extract_gallery_images(article_text_div)
            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        image_url = scrape_meta_url(soup)
        
        # updated img scraping
        if not image_url:
            target_classes = ['pub-image', 'img', 'pub-hero__photo']
            
            for cls in target_classes:
                img_div = soup.find('div', class_=cls)
                if img_div:
                    img_tag = img_div.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag['src']
                        break  
            
        
        return title, description, content, image_url,gallery_images
    else:
        return None, None, None, None,None
