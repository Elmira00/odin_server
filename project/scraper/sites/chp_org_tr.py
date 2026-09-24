import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://chp.org.tr/")
def get_news_links_chp_org_tr(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://chp.org.tr/gundem/"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    website_base_url = "https://chp.org.tr"

    news_cards = soup.find_all('a', class_='d-flex journal-allnews-news-border')    

    for news_card in news_cards:
        link = news_card['href']
        if link and link not in link_set:
            links.append(website_base_url + link)
            link_set.add(link)

    for link in links[:12]:
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_chp_org_tr(link)
        process_article_data(
            source_link="https://chp.org.tr/",
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


def fetch_article_details_chp_org_tr(url):
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

        title =title = soup.find("meta", {"name": "og:title"})
        title = title["content"] if title and title.has_attr("content") else None

        description = soup.find("meta", {"name": "og:description"})
        description = description["content"] if description and description.has_attr("content") else None

        image_url = soup.find("meta", {"name": "og:image"})
        image_url = image_url["content"] if image_url and image_url.has_attr("content") else None

        date_text = soup.find("p", class_="date effect").get_text(strip=True)
        naive_dt = datetime.strptime(date_text + " 00:00:00", "%d.%m.%Y %H:%M:%S")
        news_shared_date = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        #content

        article_text_div = soup.find("div", {"data-component": "default_column"})

        if article_text_div: 

            for div in soup.find_all("div", {"data-component": "default_youTube"}):
                div.decompose()

            #gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for ul_class in article_text_div.find_all('div', class_='twitter-tweet'):
                ul_class.decompose()

            for ul_class in article_text_div.find_all('iframe'):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
