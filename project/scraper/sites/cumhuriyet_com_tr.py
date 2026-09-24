import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images
from dateutil import parser
import pytz


from utils.decorators import check_source_active


@check_source_active("https://www.cumhuriyet.com.tr/")
def get_news_links_cumhuriyet(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = Source.objects.get(link="https://www.cumhuriyet.com.tr/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        links = [] 
        link_set = set()
        items = soup.find_all('item')
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_cumhuriyet(link)
            if not image_url:
                image_url = rss_image

            if title and content:
                process_article_data(
                source_link="https://www.cumhuriyet.com.tr/",
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


def fetch_article_details_cumhuriyet(url):
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
        description = soup.find("h2", class_="description").text.strip() if soup.find("h2", class_="description") else None
        if not description:
            description = scrape_meta_description(soup)
        
        article_div_class = soup.find('div', class_='text-content')
        if article_div_class:
                
            for image in article_div_class.find_all('img'):
                        
                if image.has_attr('src') and image['src'].startswith('/'):
                    image['src'] = "https://www.cumhuriyet.com.tr" + image['src']
                
                if image.has_attr('data-mce-src') and image['data-mce-src'].startswith('/'):
                    image['data-mce-src'] = "https://www.cumhuriyet.com.tr" + image['data-mce-src']

            gallery_images = extract_gallery_images(article_div_class)
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        image_url = scrape_meta_url(soup)
        if not image_url:
            tag = soup.find("img", class_="w-full h-full object-cover")
            if tag and tag.has_attr("src"):
                image_url = tag["src"]
        meta_tag = soup.find("meta", {"name": "datePublished"})

        if meta_tag and meta_tag.has_attr("content"):
            date_str = meta_tag["content"]
            try:
                dt = parser.isoparse(date_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                else:
                    dt = dt.astimezone(pytz.UTC)
                news_shared_date = dt
            except ValueError:
                news_shared_date = None
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
