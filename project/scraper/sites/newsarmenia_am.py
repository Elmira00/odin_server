import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
import re



from utils.decorators import check_source_active


@check_source_active("https://newsarmenia.am/")
def get_news_links_newsarmenia_am(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://newsarmenia.am/news/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []        
        
        base_website_url = "https://newsarmenia.am"
        all_news_div = soup.find('div', id='all-news')
        if all_news_div:
            
            all_a_tags = all_news_div.find_all('a', class_='news-item-title d-block')
            
            if all_a_tags:
                for a_tag in all_a_tags:
                    if a_tag.has_attr('href'):
                        link = a_tag['href']
                        links.append(base_website_url + link)
                        
                        

        for link in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date  = fetch_article_details_newsarmenia_am(link)

            process_article_data(
            source_link="https://newsarmenia.am/",
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
    

    
def fetch_article_details_newsarmenia_am(url):
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

    
        article_div_class = soup.find('div', class_='news-line-detail')
        if article_div_class:
                
            gallery_images = extract_gallery_images(article_div_class)
            clean_soup_tags(soup, article_div_class)
            content = clean_donya_e_eqtesad_com(article_div_class.prettify())
            content = clean_html_withregex(content)
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
