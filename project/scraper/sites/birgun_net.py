# import requests
# from bs4 import BeautifulSoup
# from scraper.models import NewsArticle,ChangedNewsArticle,Source
# from datetime import datetime
# from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
# from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
# from utils.process_article import process_article_data

# from utils.decorators import check_source_active


# @check_source_active("https://www.birgun.net/")
# def get_news_links_birgun(request):
#     sitemap_url = Source.objects.get(link="https://www.birgun.net/").rss_link
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
#     response = requests.get(sitemap_url, headers=headers, timeout=10)
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'xml')
#         items = soup.find_all('item')
        
#         links = [] 
#         link_set = set()
        
#         for item in items:
#             link = item.find('link').text if item.find('link') else None
#             if "/foto-galeri/" in link:
#                 continue
#             if "/makale/" in link:
#                 continue
#             title = item.find('title').text.strip() if item.find('title') else None
#             rss_image = item.find('media:content')['url'] if item.find('media:content') else None
#             pub_date = item.find('pubDate').text if item.find('pubDate') else None
#             rss_description = item.find("description").text if item.find('description') else None

#             if link and pub_date and title and rss_image and rss_description:
#                 if link not in link_set:
#                     dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
#                     links.append((link, title, dt, rss_image, rss_description))
#                     link_set.add(link)

#         for link, title, news_shared_date, image_url, rss_description in links[:30]:
#             description,content,gallery_images = fetch_article_details_birgun(link) 

#             if not description or not content:
#                 continue
            
#             process_article_data(
#                 source_link="https://www.birgun.net/",
#                 link=link,
#                 title=title,
#                 description=description,
#                 content=content,
#                 image_url=image_url,
#                 gallery_images=gallery_images,
#                 news_shared_date=news_shared_date,  
#             )
#     else:
#         return None


# def fetch_article_details_birgun(url):
#     headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

#     response = requests.get(url, headers=headers, timeout=10)
#     if response.status_code != 200:
#         return None, None, None
    
#     response.encoding = 'utf-8'  
    
#     description = None
#     content = None
#     gallery_images = [] 
    
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         if soup.find('div', attrs={'class': 'text-danger'}):
#             return None, None, None

#         description = scrape_meta_description(soup)
        
#         div_post_container = soup.find('div', class_='col-lg-8 pe-lg-4 fontsizer contentdetail')
#         if div_post_container:
#             div_class = div_post_container.find('div', class_='resize')
#             if div_class:
               
#                 gallery_images = extract_gallery_images(div_class)
#                 clean_soup_tags(soup, div_class)
#                 content = clean_donya_e_eqtesad_com(div_class.prettify())
#                 content = clean_html_withregex(content)
#         else:
#             content=None
            
#         return description, content, gallery_images
    
#     else:
#         return None, None, None







import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.birgun.net/")
def get_news_links_birgun(request):
    sitemap_url = Source.objects.get(link="https://www.birgun.net/").rss_link
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = [] 
        link_set = set()
        
        for item in items:
            link = item.find('link').text if item.find('link') else None
            if "/foto-galeri/" in link:
                continue
            if "/makale/" in link:
                continue
            title = item.find('title').text.strip() if item.find('title') else None
            rss_image = item.find('media:content')['url'] if item.find('media:content') else None
            pub_date = item.find('pubDate').text if item.find('pubDate') else None
            rss_description = item.find("description").text if item.find('description') else None

            if link and pub_date and title and rss_image and rss_description:
                if link not in link_set:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                    links.append((link, title, dt, rss_image, rss_description))
                    link_set.add(link)

        for link, title, news_shared_date, image_url, rss_description in links[:30]:
            description,content,gallery_images = fetch_article_details_birgun(link) 

            if not description or not content:
                continue
            
            process_article_data(
                source_link="https://www.birgun.net/",
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


def fetch_article_details_birgun(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None, None, None
    
    response.encoding = 'utf-8'  
    
    description = None
    content = None
    gallery_images = [] 
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('div', attrs={'class': 'text-danger'}):
            return None, None, None

        description = scrape_meta_description(soup)
        
        # div_post_container = soup.find('div', class_='col-lg-8 pe-lg-4 fontsizer contentdetail')
        # if div_post_container:
        #     div_class = div_post_container.find('div', class_='resize')
        #     if div_class:
               
        #         gallery_images = extract_gallery_images(div_class)
        #         clean_soup_tags(soup, div_class)
        #         content = clean_donya_e_eqtesad_com(div_class.prettify())
        #         content = clean_html_withregex(content)
        # else:
        #     content=None

        div_post_container = soup.find('div', class_='col-lg-8 pe-lg-4 fontsizer contentdetail')
        if div_post_container:
            gallery_images = extract_gallery_images(div_post_container)
            
            div_class = div_post_container.find('div', class_='resize')
            
            if div_class:           
                clean_soup_tags(soup, div_class)
                content = clean_donya_e_eqtesad_com(div_class.prettify())
                content = clean_html_withregex(content)
        else:
            content = None
            
        return description, content, gallery_images
    
    else:
        return None, None, None
