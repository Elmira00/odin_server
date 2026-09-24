
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz


from utils.decorators import check_source_active


@check_source_active("https://www.gercekgundem.com/")
def get_news_links_gercekgundem(request):
    sitemap_url = Source.objects.get(link="https://www.gercekgundem.com/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        
        links = [item.find('link').text for item in items if item.find('link')]

        for link in links[:50]:
            
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_gercekgundem(link)

            process_article_data(
            source_link="https://www.gercekgundem.com/",
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
    

    
def fetch_article_details_gercekgundem(url):
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
                
                
                
        #CONTENT ALMAQ UCUN
        
        div_classes=soup.find_all('div', class_='content-text',attrs={'property': 'articleBody'})

        if len(div_classes) == 1:
            div_class = div_classes[0]
            if div_class:

                gallery_images = extract_gallery_images(div_class)
                clean_soup_tags(soup, div_class)
                content = clean_donya_e_eqtesad_com(div_class.prettify())
                content = clean_html_withregex(content)
                
            else:
                content = None
                
        elif len(div_classes) > 1:
            all_content = []

            for div_class in div_classes:
                for script_tag in div_class.find_all('script'):
                    noscript_tag = soup.new_tag('noscript')
                    noscript_tag.string = script_tag.string if script_tag.string else ""
                    script_tag.replace_with(noscript_tag)

                all_content.append(div_class.prettify())

            news_content = "\n\n".join(all_content)
            
            parsed_news_content = BeautifulSoup(news_content, 'html.parser')

            gallery_images = extract_gallery_images(parsed_news_content)
            clean_soup_tags(soup, parsed_news_content)

            content = clean_donya_e_eqtesad_com(parsed_news_content.prettify())
            content = clean_html_withregex(content)

            
        elif len(div_classes) == 0:
            div_class = soup.find('div', class_='content-text unselectable',attrs={'property': 'articleBody'})
            if div_class:
                
                gallery_images = extract_gallery_images(div_class)
                clean_soup_tags(soup, div_class)
                content = clean_donya_e_eqtesad_com(div_class.prettify())
                content = clean_html_withregex(content)
                
                
                
            else:
                div_class = soup.find('div', class_='infinity-item')
                if div_class:
                    
                    gallery_images = extract_gallery_images(div_class)
                    clean_soup_tags(soup, div_class)
                    content = clean_donya_e_eqtesad_com(div_class.prettify())
                    content = clean_html_withregex(content)
                    
                else:
                    content = None
            content = None
                
        else:
            None
            
            
        #IMAGE ALMAQ UCUN
        
        div_class = soup.find('div', class_='col-12 col-lg mw-0')
        if div_class:
            figure_class = div_class.find('figure',class_='post-image')
            if figure_class:
                image = figure_class.find('img')
                image_url = image['src'] if image else None
                
            else:
                image_url = None
        else:
            gallery_items = soup.find_all('div', class_='gallery-item')
            if gallery_items:
                gallery_item = gallery_items[0]
                
                figure_tag = gallery_item.find('figure')
                if figure_tag:
                    image = figure_tag.find('img')
                    image_url = image['src'] if image else None
                else:
                    image_url = None
            else:
                image_url = None
                
                
        #Tariux almaq ucun
        
        meta_tag = soup.find("meta", {"name": "datePublished"})
        if meta_tag:
            date_str = meta_tag["content"]  

            dt = datetime.fromisoformat(date_str)

            news_shared_date = dt.astimezone(pytz.UTC)
            
        else:
            news_shared_date = None

        if not image_url:
            image_url = scrape_meta_url(soup)

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None