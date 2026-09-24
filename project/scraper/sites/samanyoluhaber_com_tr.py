import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com, extract_gallery_images
from utils.scrape_content_metatag import get_soup_from_url,scrape_clean_content,scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data



from utils.decorators import check_source_active


@check_source_active("https://www.samanyoluhaber.com/")
def get_news_links_samanyoluhaber(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://www.samanyoluhaber.com/").rss_link
    response = requests.get(sitemap_url,headers=headers)
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        
        
        items = soup.find_all('item')
        
        links = [item.find('link').text for item in items if item.find('link')]
        
        for link in links[:20]:
            
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_samanyoluhaber(link)
            
            process_article_data(
            source_link="https://www.samanyoluhaber.com/",
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
    
    
    
def fetch_article_details_samanyoluhaber(url):
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
        
        div_class = soup.find('div', class_='lb')
        
        if div_class:
            article_div_class = div_class.find('div', class_='news-text')
            if article_div_class:
                div_itemprop = article_div_class.find('div', itemprop='articleBody')
                if div_itemprop:
                    gallery_images = extract_gallery_images(div_itemprop)
                    clean_soup_tags(soup, div_itemprop)
                    content = clean_donya_e_eqtesad_com(div_itemprop.prettify())
                    content = clean_html_withregex(content)
            else:
                content = None
        else:
            content = None
        
        
        
        image_url = scrape_meta_url(soup)

            
            
        month_mapper = {
            'Ocak': 'January',
            'Şubat': 'February',
            'Mart': 'March',
            'Nisan': 'April',
            'Mayıs': 'May',
            'Haziran': 'June',
            'Temmuz': 'July',
            'Ağustos': 'August',
            'Eylül': 'September',
            'Ekim': 'October',
            'Kasım': 'November',
            'Aralık': 'December'
        }

        div_class = soup.find('div', class_='breadcrumb')

        if div_class:
            wrap_div = div_class.find('div', class_='wrap')

            if wrap_div:
                full_text = wrap_div.get_text().split('/')[-1].strip()

                for tr_month, en_month in month_mapper.items():
                    if tr_month in full_text:
                        full_text = full_text.replace(tr_month, en_month)
                        break


                try:
                    news_shared_date = datetime.strptime(full_text, "%d %B %Y %H:%M")
                except ValueError as e:
                    news_shared_date = None
            else:
                news_shared_date = None
        else:
            news_shared_date = None

            

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
    
