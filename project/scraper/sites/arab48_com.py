import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime

from utils.decorators import check_source_active


@check_source_active("https://www.arab48.com/")
def get_news_links_arab48_com(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.arab48.com/%D8%A7%D9%84%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://www.arab48.com"

    news_cards = soup.find_all('div', class_='col-md-4')    

    for news_card in news_cards:
        link = news_card.find('a')['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:18]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_arab48_com(link)
        process_article_data(
            source_link="https://www.arab48.com/",
            link=link,
            title=title,
            description=description,
            content=content,
            image_url=image_url,
            gallery_images=gallery_images,
            news_shared_date=news_shared_date
        )
        
    else:
        return None


def fetch_article_details_arab48_com(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(url,headers=headers, timeout=5)
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
        image_url = scrape_meta_url(soup)

        news_shared_date = (
            timezone.make_aware(datetime.fromisoformat(tag["content"]), timezone.get_current_timezone())
            if (tag := soup.find("meta", {"property": "article:published_time"})) and tag.has_attr("content")
            else None
        )

        #content

        article_text_div = soup.find("div", {"class": "article-content"})

        if article_text_div: 

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["div"]):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
