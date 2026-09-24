import requests
from bs4 import BeautifulSoup
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://orda.kz/")
def get_news_links_orda_kz(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://orda.kz/last-news/"
    response = requests.get(sitemap_url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []        
        
        base_website_url = "https://orda.kz"
        
        div_class = soup.find('div', class_='newslist3')
        if div_class:
            ul_class = div_class.find('ul')
            if ul_class:
                li_tags = ul_class.find_all('li')               
                if li_tags:
                    for li_tag in li_tags:
                        a_tag = li_tag.find('a')
                        if a_tag and a_tag.has_attr('href'):
                            link = a_tag['href']
                            links.append(base_website_url + link)
                        
        for link in links[:30]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_orda_kz(link)

            process_article_data(
                source_link="https://orda.kz/",
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
    

def fetch_article_details_orda_kz(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url,headers=headers, timeout=10)
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
        image_url = scrape_meta_url(soup)
        
        #Content
        div_class = soup.find('div', class_='fulltext')
        if div_class:
            article_div_class = div_class.find('div', class_='newstext')
            if article_div_class:
                
                for script_tag in article_div_class.find_all('script'):
                    script_tag.decompose()
                    
                base_website_url = 'https://orda.kz'

                # for image in article_div_class.find_all('img'):
                #     if not image.get_text(strip=True):
                #         if image and image.has_attr('src'):
                #             src = image['src']
                #             if not src.startswith('http'):
                #                 src = base_website_url.rstrip('/') + '/' + src.lstrip('/')
                #             new_img_tag = soup.new_tag('img', src=src)
                #             image.replace_with(new_img_tag)
                #         else:
                #             image.decompose()
                #     else:
                #         image.decompose()
    
                for p_tag in article_div_class.find_all('p'):
                    b_tag = p_tag.find('b')
                    if b_tag and 'Читайте также:' in b_tag.get_text(strip=True):
                        p_tag.decompose()
                        
                all_ul_tags = article_div_class.find_all('ul')
                last_ul_tag = all_ul_tags[-1] if all_ul_tags else None
                if last_ul_tag: 
                    last_ul_tag.decompose()
   
                gallery_images = extract_gallery_images(article_div_class)
                gallery_images = ["https://orda.kz" + image for image in gallery_images if image.startswith('/')]
                clean_soup_tags(soup, article_div_class)
                content = clean_donya_e_eqtesad_com(article_div_class.prettify())
                content = clean_html_withregex(content)    
            else:
                content = None
        else:
            content = None
        
        # base_website_url='https://orda.kz'
        # inner_image_div = soup.find('div', class_='postpic')
        # if inner_image_div:
        #     image = inner_image_div.find('img')
        #     image_url_first = image['src'] if image else None
        #     image_url = base_website_url+image_url_first
        # else:
        #     image_url = None

        tag = soup.find("time", {"itemprop": "datePublished"})
        if tag and tag.has_attr("datetime"):
            news_shared_date = tag["datetime"]
        else:
            news_shared_date = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
