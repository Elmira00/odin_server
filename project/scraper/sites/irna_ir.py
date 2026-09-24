import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from dateutil import parser
import pytz
import re
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.infox.ru/")
def get_news_links_irna_ir(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = "https://www.irna.ir/rss"
    response = requests.get(sitemap_url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        
        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_irna_ir(link)
            
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

        
        
        
def fetch_article_details_irna_ir(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'  
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        
        meta_tag_title = soup.find("meta", {"property": "og:title"})
        title = meta_tag_title["content"] if meta_tag_title and "content" in meta_tag_title.attrs else None

        # Açıqlama (description)
        meta_tag_desc = soup.find("meta", {"property": "og:description"})
        description = meta_tag_desc["content"] if meta_tag_desc and "content" in meta_tag_desc.attrs else " "


        #content     
        div_class = soup.find('div',class_ = 'item-body')
        if div_class:
            
            if div_class:

                for script_tag in div_class.find_all('script'):
                    script_tag.decompose()

                for image in div_class.find_all('img'):
                    if image and image.has_attr('src'):
                        new_img_tag = soup.new_tag('img', src=image['src'])
                        image.replace_with(new_img_tag)
                    else:
                        image.decompose() 
                            
                        
                for video_tag in div_class.find_all('video'):
                    source_tag = video_tag.find('source')
                    if source_tag and source_tag.has_attr('src'):
                        new_video_tag = soup.new_tag('video', controls=True)
                        new_source_tag = soup.new_tag('source', src=source_tag['src'])
                        new_video_tag.append(new_source_tag)
                        video_tag.replace_with(new_video_tag)
                    else:
                        video_tag.decompose()
                        
                for a_tag in div_class.find_all('a'):
                    if a_tag and a_tag.has_attr('href'):
                        new_a_tag = soup.new_tag('a', href=a_tag['href'])
                        new_a_tag.string = a_tag.get_text(strip=True)
                        a_tag.replace_with(new_a_tag)
                    else:
                        a_tag.decompose()
                        
                        
                for iframe in div_class.find_all('iframe'):
                    if not iframe.get_text(strip=True):
                        if iframe and iframe.has_attr('src'):
                            new_img_tag = soup.new_tag('iframe', src=iframe['src'])
                            iframe.replace_with(new_img_tag)
                        else:
                            iframe.decompose() 
                    else:
                        iframe.decompose() 
                        
                        
                for div in div_class.find_all('div',class_ = "ts-fab-wrapper ts-fab-icons-text"):
                        
                    div.decompose() 
                    
                for div in div_class.find_all('div',id = "inline-related-post"):
                    
                    div.decompose()
                        
                            
                content = description + clean_armenianweekly_com(div_class.prettify())

                # 1. tam boş div’leri sil
                content = re.sub(r'<div>\s*</div>', '', content)

                # 2. İçinde sadece boş <div> olan div’leri sil
                content = re.sub(r'<div>\s*(<div>\s*</div>\s*)+\s*</div>', '', content)

                # 3. Sadece <svg> olan div’leri sil
                content = re.sub(r'<div>\s*<svg[^>]*?>[\s\S]*?</svg>\s*</div>', '', content)

                # 4. İç içe sadece boş div zincirlerini sil
                content = re.sub(r'(<div>\s*){2,}(</div>\s*){2,}', '', content)

                # 5. bircen cox setiri tek setirde 
                content = re.sub(r'\n\s*\n+', '\n', content)

                content = re.sub(r'<\s*br\s*/?>', ' ', content, flags=re.IGNORECASE)
                
                content = re.sub(r'<\s*/?\s*o:p\s*>', '', content, flags=re.IGNORECASE)

                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

                content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)
            else:
                content = None
        else:
            content = None


        # Şəkil URL-ni göstər
        meta_tag_image_tag = soup.find("meta", {"property": "og:image"})
        image_url = meta_tag_image_tag["content"] if meta_tag_image_tag and "content" in meta_tag_image_tag.attrs else None

        # Tarix
        meta_tag = soup.find("meta", attrs={"itemprop": "datePublished"})
        if not meta_tag:
            meta_tag = soup.find("meta", attrs={"property": "article:published_time"})

        
        if meta_tag:
            date_str = meta_tag["content"] 
            dt_utc = parser.parse(date_str)  
            baku_tz = pytz.timezone("Asia/Baku")
            news_shared_date = dt_utc.astimezone(baku_tz)
        else:
            news_shared_date = None


        return title, content, image_url, news_shared_date
    else:
        return None, None, None ,None
