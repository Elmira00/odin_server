import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
import pytz
from dateutil import parser
import re
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://centralasia.media/")
def get_news_links_centralasia_media(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://centralasia.media/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        links = [] 
        link_set = set()
        
        items = soup.find_all('item')
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link :
                if link not in link_set:
                    
                    links.append((link))
                    link_set.add(link)
        
        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_centralasia_media(link)
            
            process_article_data(
            source_link="https://centralasia.media/",
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



def fetch_article_details_centralasia_media(url):
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
        
        
        # Content
        div_class = soup.find('div', class_='newstext')
        if div_class:
            
            for style_tag in div_class.find_all('style'):
                style_tag.decompose()
            
            div_classes = div_class.find_all('div')
            first_div = div_classes[0] if div_classes else None
            if first_div:
                first_div.decompose()
                    
            

            aki_div_class = div_class.find('div', class_='aki_gallery_insert_place')
            if aki_div_class:
                thumbs = aki_div_class.find_all('div', class_=re.compile(r'aki_gallery_thumb_\d+'))
                for thumb in thumbs:
                    style = thumb.get('style', '')
                    match = re.search(r'url\((.*?)\)', style)
                    if match:
                        url = match.group(1)
                        url = re.sub(r'\.0(?=\.\w{3,4}$)', '', url)
                        gallery_images.append(url)
                
                    
            image_prefix= "https:"
            
            for image in div_class.find_all('img'):
                src = None
                if image.has_attr('data-src'):
                    src = image['data-src'].strip()
                elif image.has_attr('src'):
                    src = image['src'].strip()
                
                if src:
                    if src.startswith("/"):
                        src = image_prefix + src
                    
                    gallery_images.append(src)

                image.decompose()
            
            for div in div_class.find_all("div"):
                text = div.get_text(strip=True)
                if re.search(r'За событиями следите.*?Телеграм-канале', text):
                    div.decompose()

                
            for a_tag in div_class.find_all('a',id = 'covid-bottom-block'):
                a_tag.decompose()

            
                
            clean_soup_tags(soup, div_class)
            content = clean_donya_e_eqtesad_com(div_class.prettify())
            content = clean_html_withregex(content)

            
        else:
            content = None

        
        image_url = scrape_meta_url(soup)

        
        
        # Time
        meta_tag = soup.find("meta", {"property":"article:published_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
