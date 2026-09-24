import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.ulusal.com.tr/")
def get_news_links_ulusal(request):
    sitemap_url = Source.objects.get(link="https://www.ulusal.com.tr/").rss_link
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        links = []
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            title = item.find('title').text.strip() if item.find('title') else None
            pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else None
            description = item.find("description").text.strip() if item.find("description") else None

            if link and pub_date and title and description:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                description = BeautifulSoup(description, "html.parser")
                rss_image = description.find("img")["src"] if description.find("img") else None
                description = description.find("h4").get_text(strip=True) if description.find("h4") else None
                links.append((link, title, dt, description, rss_image)) 

        for link, title, news_shared_date, description, rss_image in links[:20]:
            if "/market/" in link:
                continue
            content, image_url, gallery_images = fetch_article_details_ulusal(link)
            if not image_url:
                image_url = rss_image
            
            process_article_data(
                source_link="https://www.ulusal.com.tr/",
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


def fetch_article_details_ulusal(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers, timeout=10)
    if response.url != url:
        return None, None, None, None, None
    response.encoding = 'utf-8'  
    
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        h2_clll = soup.find('h2', class_='post-detail-summary')
        description = h2_clll.get_text(strip=True) if h2_clll else None
        
        gallery_items = soup.find_all('div', class_='gallery-item')
        content = ""

        if gallery_items:
            for item in gallery_items:
                if item:
                    for media_tag in item.find_all('div', class_='media-block also-read'):
                        media_tag.decompose()

                    gallery_images += extract_gallery_images(item)

                    soup_inner = BeautifulSoup(item.prettify(), "html.parser")
                    container = soup_inner.body or soup_inner
                    clean_soup_tags(soup_inner, container)

                    final_content = clean_donya_e_eqtesad_com(str(container))
                    final_content = clean_html_withregex(final_content)

                    content += final_content + " "
        else:
            article_class = soup.find('article', class_='post-detail')
            if article_class:
                div_class = article_class.find('div', class_='content-text')
                if div_class:
                    for media_tag in div_class.find_all('div', class_='media-block also-read'):
                        media_tag.decompose()

                    for suggest_div in div_class.find_all('div', class_='mceNonEditable related-news'):
                        suggest_div.decompose()

                    gallery_images = extract_gallery_images(div_class)
                    clean_soup_tags(soup, div_class)
                    content = clean_donya_e_eqtesad_com(div_class.prettify())
                    content = clean_html_withregex(content)

        image_url = scrape_meta_url(soup)
            
        return  content, None, gallery_images
    else:
        return None, None, None
