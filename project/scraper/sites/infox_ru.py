import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://www.infox.ru/")
def get_news_links_infoxru(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://www.infox.ru/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')

 
        items = soup.find_all('item')

        links = [item.find('link').text for item in items if item.find('link')]

        for link in links[:30]:

            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_infoxru(link)

            process_article_data(
            source_link="https://www.infox.ru/",
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
 
     
    
     
    
def fetch_article_details_infoxru(url):
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
        if not title:
            title_tag = soup.find('h1', {'itemprop': 'headline'})
            title = title_tag.get_text(strip=True) if title_tag else None
        description = scrape_meta_description(soup)
        



        div_class = soup.find('div', class_='col5-3-5 col4-3-4 col3-1-1 col content_article over_float')
        if div_class:
            article_class = div_class.find('article', class_='clx')
            if article_class:
        
                news_content = article_class.find('div', {'itemprop': 'articleBody'})
                if news_content:
                    
                    gallery_images = extract_gallery_images(news_content)
                    clean_soup_tags(soup, news_content)
                    content = clean_donya_e_eqtesad_com(news_content.prettify())
                    content = clean_html_withregex(content)
                        
                else:
                    content = None
            else:
                content = None
                
        else:
            content = None
            
            
        
        image_url = scrape_meta_url(soup)
        
        
        div_class = soup.find('div', class_='col5-3-5 col4-3-4 col3-1-1 col content_article over_float')
        if div_class:
            article_class = div_class.find('article', class_='clx')
            if article_class:
                author_div = article_class.find('div', class_='autor')
                if author_div:
                    author_pd_class = author_div.find('div', class_="autor_pd")
                    if author_pd_class:
                        time_tag = author_pd_class.find('time', itemprop='datePublished')
                        if time_tag:
                            datetime_str = time_tag.get('datetime')
                            try:
                                news_shared_date = datetime.fromisoformat(datetime_str)
                            except ValueError as e:
                                news_shared_date = None
                        else:
                            news_shared_date = None
                    else:
                        news_shared_date = None
                else:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    
