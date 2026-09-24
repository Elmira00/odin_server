
import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
import pytz
from dateutil import parser
from datetime import timedelta
import re


from utils.decorators import check_source_active


@check_source_active("https://rasthaber.com/")
def get_news_links_rasthaber(request):
    sitemap_url = "https://rasthaber.com/"
    response = requests.get(sitemap_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []

        website_base_url = "https://rasthaber.com"

        table_div = soup.find('div', class_='tab-pane fade show active')
        if table_div:
            table_class = table_div.find('table',class_="table table-hover")
            if table_class:    
                t_body = soup.find_all('tbody')
                main_t_body = t_body[1]
                if main_t_body:
                    trs = main_t_body.find_all('tr')
                    if trs:
                        for tr in trs:
                            td_classes = tr.find_all('td')
                            if td_classes:
                                first_td = td_classes[0]
                                
                                if first_td:
                                    a_tag = first_td.find('a')
                                    if a_tag and a_tag.has_attr('href'):
                                        link = a_tag['href']
                                        links.append(website_base_url+link)
                                        
        

        for link in links[:10]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_rasthaber(link)

            process_article_data(
            source_link="https://rasthaber.com/",
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
    
    

def fetch_article_details_rasthaber(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title = scrape_meta_title(soup)


        #description almaq
        
        
        div_class_md = soup.find('div', class_='col-sm-12 col-md-8')
        if div_class_md:
            card_class = div_class_md.find('div',class_='card')
            if card_class:
                description = card_class.find('div',class_='article-description')
                description = description.get_text(strip=True) if description else None
            else:
                description = None
        else:
            description = None

        
        
        
        #content almaq
        
        
        div_class_md = soup.find('div', class_='col-sm-12 col-md-8')
        if div_class_md:
            card_class = div_class_md.find('div',class_='card')
            if card_class:
                card_body_class = card_class.find('div',class_='card-body')
                if card_body_class:
                    section_tag = card_body_class.find('section',id='section-article')
                    if section_tag:
                        gallery_images = extract_gallery_images(section_tag)
                        clean_soup_tags(soup, section_tag)
                        content = clean_donya_e_eqtesad_com(section_tag.prettify())
                        content = clean_html_withregex(content)
                    else:
                        content = None
                else:
                    content = None
            else:
                content = None
        else:
            content = None
        
        
        
        image_url = scrape_meta_url(soup)
                    
                    
            
            
        div_class_md = soup.find('div', class_='col-sm-12 col-md-8')
        if div_class_md:
            card_class = div_class_md.find('div',class_='card')
            if card_class:
                card_body_class = card_class.find('div',class_='card-body')
                if card_body_class:
                    md_div = card_body_class.find('div',class_='col-sm-12 col-md-7')
                    if md_div:
                        small_tag = md_div.find('small')
                        if small_tag:
                            text = small_tag.get_text(strip=True)  

                            dates = re.findall(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}', text)

                            if dates:
                                dt = parser.parse(dates[0])  
                                dt = dt + timedelta(hours=1)  
                                news_shared_date = dt  
                            else:
                                news_shared_date = None
                    else:
                        news_shared_date = None
                        

        return title,description, content, image_url,gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
