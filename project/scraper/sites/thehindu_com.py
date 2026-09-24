# rss: https://www.thehindu.com/news/international/feeder/default.rss
# region: Canada
import requests
from bs4 import BeautifulSoup
from scraper.models import Source

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.thehindu.com/")
def get_news_links_thehindu_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.thehindu.com/").rss_link
    headers  = {"User-Agent":"Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
        
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link :
                if link not in link_set:
                    links.append((link))
                    link_set.add(link)
                
        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_thehindu_com(link)
            
            process_article_data(
                source_link="https://www.thehindu.com/",
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
    

def fetch_article_details_thehindu_com(url):
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
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find("meta", {"name": "publish-date"})["content"]

  
        article_text_div = soup.find("div", class_="schemaDiv")

        if article_text_div: 

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('ul', class_='gallery_attach_list'):
                ul_class.decompose()

            for fc_tag in article_text_div.find_all('figure'):
                fc_tag.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
     
