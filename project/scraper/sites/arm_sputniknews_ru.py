import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import extract_relevant_content,clean_uz_sputniknews_ru
import pytz
from dateutil import parser
import re
from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images


from utils.decorators import check_source_active


@check_source_active("https://arm.sputniknews.ru")
def get_news_links_arm_sputniknews_ru(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://arm.sputniknews.ru/news/"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        
        website_base_url = "https://arm.sputniknews.ru"
    
    
        infinite_class = soup.find_all('div', class_='list__content')    
        if infinite_class:
            for infinite in infinite_class:
                a_class = infinite.find('a', class_='list__title')
                if a_class and a_class.has_attr('href'):
                    link = a_class['href']
                    links.append(website_base_url + link)

        for link in links[:20]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_arm_sputniknews_ru(link)
            process_article_data(
            source_link="https://arm.sputniknews.ru",
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
    

    
def fetch_article_details_arm_sputniknews_ru(url):
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

    
        
        article_text_div = soup.find('div', class_='article__body')
        if article_text_div:

            for script_tag in article_text_div.find_all('script'):
                script_tag.decompose()

            

            main_photo_divs = soup.find_all("div", attrs={"class": "article__block", "data-article": "main-photo"})
            for div in main_photo_divs:
                div.decompose()
                
            cleaned_blocks = []
            for block in article_text_div.find_all("div", class_="article__block", recursive=False):
                inner_content = block.find("div", recursive=False)
                if inner_content:
                    cleaned_blocks.append(inner_content.prettify())  
                    
                    

            first_cleaned_block_html = "\n".join(cleaned_blocks)
            first_cleaned_block_soup = BeautifulSoup(first_cleaned_block_html, 'html.parser')
            
            
            gallery_images = extract_gallery_images(first_cleaned_block_soup)
            clean_soup_tags(soup, first_cleaned_block_soup)
            content = clean_donya_e_eqtesad_com(first_cleaned_block_soup.prettify())
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
    
    
    
    
    
    
    
    
    
# def fetch_article_details_arm_sputniknews_ru(url):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

#     response = requests.get(url,headers=headers)
#     response.encoding = 'utf-8'  
    
#     title = None
#     content = None
#     image_url = None
#     news_shared_date = None
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         meta_tag_title = soup.find("meta", {"property": "og:title"})
#         title = meta_tag_title["content"] if meta_tag_title and "content" in meta_tag_title.attrs else None

#         # Açıqlama (description)
#         meta_tag_desc = soup.find("meta", {"property": "og:description"})
#         description = meta_tag_desc["content"] if meta_tag_desc and "content" in meta_tag_desc.attrs else " "


#         #content     

#         article_text_div = soup.find('div', class_='article__body')
#         if article_text_div:

#             # script tag'lərini sil və ya dəyişdir
#             for script_tag in article_text_div.find_all('script'):
#                 noscript_tag = soup.new_tag('noscript')
#                 noscript_tag.string = script_tag.string if script_tag.string else ""
#                 script_tag.replace_with(noscript_tag)
                
#             for noscript_tag in article_text_div.find_all('noscript'):
#                 noscript_tag.decompose()

#             for image in article_text_div.find_all('img'):
#                 if not image.get_text(strip=True):
#                     if image and image.has_attr('src'):
#                         new_img_tag = soup.new_tag('img', src=image['src'])
#                         image.replace_with(new_img_tag)
#                     else:
#                         image.decompose() 
#                 else:
#                     image.decompose() 

#             main_photo_divs = soup.find_all("div", attrs={"class": "article__block", "data-article": "main-photo"})
#             for div in main_photo_divs:
#                 div.decompose()
                
#             for a_tag in article_text_div.find_all('a'):
#                 if a_tag and a_tag.has_attr('href'):
#                     new_a_tag = soup.new_tag('a', href=a_tag['href'])
#                     new_a_tag.string = a_tag.get_text(strip=True)
#                     a_tag.replace_with(new_a_tag)
#                 else:
#                     a_tag.decompose()

#             cleaned_blocks = []
#             for block in article_text_div.find_all("div", class_="article__block", recursive=False):
#                 inner_content = block.find("div", recursive=False)
#                 if inner_content:
#                     cleaned_blocks.append(inner_content.prettify())  

#             first_cleaned_block = "\n".join(cleaned_blocks)
            
#             content = description + clean_uz_sputniknews_ru(first_cleaned_block)
            
#             content = re.sub(r'<div>\s*</div>', '', content)

#             content = re.sub(r'<div>\s*(<div>\s*</div>\s*)+\s*</div>', '', content)

#             content = re.sub(r'<div>\s*<svg[^>]*?>[\s\S]*?</svg>\s*</div>', '', content)

#             content = re.sub(r'(<div>\s*){2,}(</div>\s*){2,}', '', content)

#             content = re.sub(r'\n\s*\n+', '\n', content)

#             content = re.sub(r'<\s*br\s*/?>', ' ', content, flags=re.IGNORECASE)
            
#             content = re.sub(r'<\s*/?\s*o:p\s*>', '', content, flags=re.IGNORECASE)

#             content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

#             content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)
            
#         else:
#             content = None



#         # Şəkil URL-ni göstər
#         meta_tag_image_tag = soup.find("meta", {"property": "og:image"})
#         image_url = meta_tag_image_tag["content"] if meta_tag_image_tag and "content" in meta_tag_image_tag.attrs else None

#         # Tarix
#         meta_tag_date_tag = soup.find("meta", {"property": "article:published_time"})
#         if meta_tag_date_tag:
#             date_str = meta_tag_date_tag["content"]
#             dt = parser.parse(date_str)  
#             news_shared_date = dt.astimezone(pytz.UTC)
#         else:
#             news_shared_date = None

#         return title, content, image_url, news_shared_date
#     else:
#         return None, None, None ,None
