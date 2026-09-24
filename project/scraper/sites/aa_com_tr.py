import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from utils.decorators import check_source_active


@check_source_active("https://www.aa.com.tr/tr/")
def get_news_links_aa(request):
    headers  = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    sitemap_url = Source.objects.get(link="https://www.aa.com.tr/tr/").rss_link
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        links = []
        link_set = set()

        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            title = item.find('title').text.strip() if item.find('title') else None
            description = item.find('description').text.strip() if item.find('description') else None
            pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else None
            image = item.find('image').text.strip() if item.find('image') else None

            if link and pub_date and title and description and image:
                if link not in link_set:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                    links.append((link, title, description, dt, image))
                    link_set.add(link)

        for link, title, description, news_shared_date, image_url in links[:30]:
            content, gallery_images = fetch_article_details_aa(link)

            process_article_data(
            source_link="https://www.aa.com.tr/tr/",
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

    
    
def fetch_article_details_aa(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers, timeout=5)
    
    response.encoding = 'utf-8'  
    
    content = None
    gallery_images = [] 
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        
        article_text_div = soup.find('div', class_='detay-icerik')

        
        if article_text_div:
            
            unwanted_div_classes = ["detay-paylas"]

            for div_class in unwanted_div_classes:
                for div in article_text_div.find_all("div", class_=div_class):
                    div.decompose()
            
            unwanted_span_class = ["detay-foto-editor"]

            for span_class in unwanted_span_class:
                for span in article_text_div.find_all("span", class_=span_class):
                    span.decompose()
                    
            

            for div in soup.find_all("div", recursive=True):
                style = div.get("style", "")
                text = div.get_text(strip=True)

                if (
                    "border:1px solid #0077b6" in style and
                    "background-color:#e6f2fa" in style and
                    "AA'nın WhatsApp kanallarına katılın" in text
                ):
                    div.decompose()
                    break  
                
            for style_tag in article_text_div.find_all("style"):
                style_tag.decompose()

            cdn_prefix = "https://cdnuploads.aa.com.tr/"

            for image in article_text_div.find_all('img'):
                if image and image.has_attr('src'):
                    src = image['src'].strip()

                    if not src.startswith(('http://', 'https://')):
                        src = cdn_prefix + src.lstrip('/')

                    gallery_images.append(src)
                image.decompose()

            
            clean_soup_tags(soup, article_text_div)
                        
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())

            content = clean_html_withregex(content)
            
            
        else:
            content = None

            
        return content,gallery_images
    else:
        return None
