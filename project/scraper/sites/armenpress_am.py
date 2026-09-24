import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime,timedelta
from dateutil import parser
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz


from utils.decorators import check_source_active


@check_source_active("https://armenpress.am/hy")
def get_news_links_armenpress_am(request):
    sitemap_url = Source.objects.get(link="https://armenpress.am/hy").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        link_set = set()
         
        for item in items:
            link = item.find('link').text if item.find('link') else None
            pub_date = item.find('pubDate').text if item.find('pubDate') else None

            if link and pub_date:
                if link not in link_set:
                    dt = parser.parse(pub_date).astimezone(pytz.UTC)
                    links.append((link, dt))
                    link_set.add(link)

        for link, news_shared_date in links[:30]:
            title,description, content, image_url,gallery_images = fetch_article_details_armenpress_am(link)
            
            process_article_data(
            source_link="https://armenpress.am/hy",
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

    
    
def fetch_article_details_armenpress_am(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers)
    
    response.encoding = 'utf-8'  
    
    title = None
    description = None
    content = None
    gallery_images = [] 
    image_url = None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = scrape_meta_title(soup)
        description = scrape_meta_description(soup)
                        
        content_div = soup.find('div', class_='w-full prose dark:prose-invert prose-base prose-slate prose-a:text-blue-600 prose-blockquote:relative prose-blockquote:my-14 prose-blockquote:border-0 prose-blockquote:pl-6 prose-blockquote:font-heading prose-blockquote:text-lg prose-blockquote:italic prose-figcaption:text-sm prose-figcaption:text-slate-400 prose-strong:leading-[unset] mt-7')

        if content_div:

            gallery_images = extract_gallery_images(content_div)
            clean_soup_tags(soup, content_div)
            content = clean_donya_e_eqtesad_com(content_div.prettify())
            content = clean_html_withregex(content)
                                
        else:
            content = None 
            
            
        image_url = scrape_meta_url(soup)


        return title, description, content, image_url,gallery_images
    
    else:
        return None, None, None, None,None
