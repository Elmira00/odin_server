# rss: https://www.theguardian.com/world/rss
# region: United Kingdom
import requests
from bs4 import BeautifulSoup
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.theguardian.com/international")
def get_news_links_theguardian_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.theguardian.com/international").rss_link
    headers  = {"User-Agent":"Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None
            if "/live/" in link:
                continue
            if "/audio/" in link:
                continue
            rss_image = item.find("media:content")["url"].strip() if item.find("media:content") and item.find("media:content").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)
                
        for link, rss_image in links[:40]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_theguardian_com(link)
            
            process_article_data(
                source_link="https://www.theguardian.com/international",
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
    

def fetch_article_details_theguardian_com(url):
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
        news_shared_date = scrape_meta_news_shared_date(soup)
        image_url = scrape_meta_url(soup)

        #content   
  
        article_text_div = soup.find("div", class_="dcr-ydnaza")
        if not article_text_div:
            article_text_div = soup.find("div", class_="article-body-commercial-selector")

        if article_text_div:     

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            CLASS_MATCHES = {
                'div': [
                    "dcr-1t8m8f2",
                ],
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in soup.find_all(tag_name, class_=class_name):
                        tag.decompose()

            for fc_tag in article_text_div.find_all('figcaption'):
                fc_tag.decompose()

            for fig_tag in article_text_div.find_all('figure'):
                fig_tag.decompose()

            for gu_tag in article_text_div.find_all('gu-island'):
                gu_tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    