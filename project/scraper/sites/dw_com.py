import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime,timedelta
from utils.clean_content import clean_agos,clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://www.dw.com/tr")
def get_news_links_dwcom(request):
    sitemap_url = Source.objects.get(link="https://www.dw.com/tr").rss_link
    response = requests.get(sitemap_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        links = [] 
        link_set = set()
        
        for item in items:
            link = item.find('link').text if item.find('link') else None
            pub_date = item.find('dc:date').text if item.find('dc:date') else None

            if link and pub_date:
                if link not in link_set:
                    dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    dt = dt + timedelta(hours=1) 
                    links.append((link, dt))
                    link_set.add(link)
        
        for link, news_shared_date in links[:15]:
            title,description, content, image_url,gallery_images = fetch_article_details_dwcom(link)

            process_article_data(
            source_link="https://www.dw.com/tr",
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


    
    
def fetch_article_details_dwcom(url):
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
                    
            
        
        # Content Alma
        div_class = soup.find('div',class_='content-area sa7l9jt s9mg977')
        if div_class:
            inner_div = div_class.find('div',class_='cc0m0op s1ebneao rich-text t1it8i9i r1wgtjne wgx1hx2 b1ho1h07')
            if inner_div:
                for p in inner_div.find_all('p'):
                    a_tag = p.find('a')
                    text_match = "DW Türkçe'ye engelsiz nasıl ulaşabilirim" in p.get_text(strip=True)

                    if a_tag or text_match:
                        p.decompose()

                gallery_images = extract_gallery_images(inner_div)
                clean_soup_tags(soup, inner_div)
                content = clean_donya_e_eqtesad_com(inner_div.prettify())
                content = clean_html_withregex(content)
        else:
            content=None
                
                
                          
        image_url = scrape_meta_url(soup)
            
        return title, description, content, image_url,gallery_images
    
    else:
        return None, None, None, None,None

