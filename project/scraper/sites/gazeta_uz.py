import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser

from utils.decorators import check_source_active


@check_source_active("https://www.gazeta.uz/oz/")
def get_news_links_gazeta_uz(request):
    sitemap_url = Source.objects.get(link="https://www.gazeta.uz/oz/").rss_link
    headers  = {"User-Agent":"Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)
                
        for link, rss_image in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_gazeta_uz(link)
            if not image_url:
                image_url = rss_image

            process_article_data(
                source_link="https://www.gazeta.uz/oz/",
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
    

def fetch_article_details_gazeta_uz(url):
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
        if not title:
            title_tag = soup.find('h1', id='article_title')
            title = title_tag.get_text(strip=True) if title_tag else None

        # 2-ci struktur uchun title
        if not title:
            title_tag = soup.find('div', {'field': 'title'})
            title = title_tag.get_text(strip=True) if title_tag else None

        description = scrape_meta_description(soup)
        if not description:
            desc_tag = soup.find('div', class_='t-descr')
            description = desc_tag.get_text(separator=' ', strip=True) if desc_tag else None

        # 2-ci struktur uchun description
        if not description:
            desc_tag = soup.find('div', class_='t-text', attrs={'field': 'text'})
            description = desc_tag.get_text(separator=' ', strip=True) if desc_tag else None

        # 3-cü Cəhd (Afisha tipli, t-text)
        if not description:
            desc_tag = soup.find('div', class_='t-text', attrs={'field': 'text'})
            description = desc_tag.get_text(separator=' ', strip=True) if desc_tag else None

        # content
        article_div_class = None

        # 1-ci nov struktur(standart) uchun
        article_div_class = soup.find('div', class_='js-mediator-article article-text')
        # 2-ci nov struktur(Tilda/Longread) uchun
        if not article_div_class:
            article_div_class = soup.find('div', id='allrecords')

        if article_div_class:
            for a_tag in article_div_class.find_all('a', href='/reklama'):
                a_tag.decompose()

            gallery_images = extract_gallery_images(article_div_class)
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
        
        image_url = scrape_meta_url(soup)

        #tarix
        meta_tag = soup.find("meta", {"property":"article:published_time"})
        if meta_tag:
            date_str = meta_tag["content"]
            dt = parser.parse(date_str)  
            news_shared_date = dt.astimezone(pytz.UTC)
        else:
            return None, None, None, None, None, None
            
        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
