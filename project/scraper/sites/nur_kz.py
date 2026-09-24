import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import re



from utils.decorators import check_source_active


@check_source_active("https://www.nur.kz/")
def get_news_links_nur_kz(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.nur.kz/latest/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    
        links = []        
        
        ul_list = soup.find('ul', class_='latest-news')
        if ul_list:
            li_classes = ul_list.find_all('li', class_='latest-news__article')
            if li_classes:
                for li_class in li_classes:                
                    if li_class:
                        article_class = li_class.find('article', class_='js-article article-card article-card--all-news')
                        if article_class:
                            a_class = article_class.find('a')
                            if a_class and a_class.has_attr('href'):
                                link = a_class['href']
                               
                                links.append(link)

        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_nur_kz(link)

            process_article_data(
            source_link="https://www.nur.kz/",
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
    

    
def fetch_article_details_nur_kz(url):
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
        
        content_div = soup.find('div', class_='formatted-body__content--wrapper')
        if content_div:
            
           
            for aside_tag in content_div.find_all('aside', class_='adv-placeholder adv-placeholder--in-article'):
                aside_tag.decompose()
                
            for div_id in content_div.find_all('div', id='js-adfox-scrollroll'):\
                div_id.decompose()

            for style_tag in content_div.find_all('style'):
                style_tag.decompose()
                
            for section_tag in content_div.find_all('section',class_='subscription'):
                section_tag.decompose()
                
            for p_class in content_div.find_all('p', class_='info-link-container astro-snohcbaj'):
                p_class.decompose()
            
            gallery_images = extract_gallery_images(content_div)
            
            for figure_class in content_div.find_all('figure', class_='article-picture__container article-picture__container--with-placeholder js-article-cover-image'):
                figure_class.decompose()
                
                
            
                
            
            
            clean_soup_tags(soup, content_div)
            content = clean_donya_e_eqtesad_com(content_div.prettify())
            content = clean_html_withregex(content)
            
        else:
            content = None
        
        picture_tag = soup.find('picture')
        if picture_tag:
            img_tag = picture_tag.find('img', class_="inline-picture")
            image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
        else:
            image_url = None

        # Publication time
        news_shared_date = None
        meta_tag = soup.find("meta", {"property":"article:published_time"})
        if meta_tag and 'content' in meta_tag.attrs:
            date_str = meta_tag["content"]
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                news_shared_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                news_shared_date = None
            
            
        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
        
