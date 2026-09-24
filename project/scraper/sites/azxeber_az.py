import requests
from bs4 import BeautifulSoup
from scraper.models import NewsArticle,ChangedNewsArticle,Source
from datetime import datetime

from utils.process_article import process_article_data
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url
from utils.clean_content import clean_donya_e_eqtesad_com,clean_html_withregex,clean_soup_tags,extract_gallery_images

from utils.decorators import check_source_active


@check_source_active("https://azxeber.com/")
def get_news_links_azxeber(request):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    sitemap_url = Source.objects.get(link="https://azxeber.com/").rss_link
    response = requests.get(sitemap_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all("item")
        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            rss_image = item.find("enclosure")["url"] if item.find("enclosure") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:20]:
            title,description, content, image_url,gallery_images,news_shared_date = fetch_article_details_azxeber(link)
            if not image_url:
                image_url = rss_image
            
            process_article_data(
                source_link="https://azxeber.com/",
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


def fetch_article_details_azxeber(url):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers, timeout=10)
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
        news_shared_date = soup.find("meta", {"itemprop": "datePublished"})["content"] if soup.find("meta", {"itemprop": "datePublished"}) else None
        
        meta_desc_tag = soup.find("meta", {"name": "description"})
        description = meta_desc_tag["content"] if meta_desc_tag and "content" in meta_desc_tag.attrs else None

        content_element = soup.find('div', class_='full-post-article')
        if content_element:
            article_text_div = content_element.find('article', class_='article-full-story')
            if article_text_div:
                
                for tag in article_text_div.find_all(['meta', 'script', 'style', 'link']):
                    tag.decompose()

                for tag in article_text_div.find_all(class_=['ainsyndication', 'nitro-lazy', 'post-meta', 'entry-meta']):
                    tag.decompose()

                for tag in article_text_div.find_all(attrs={"itemprop": True}):
                    tag.decompose()

                gallery_images = extract_gallery_images(article_text_div)

                clean_soup_tags(soup, article_text_div)
                content = clean_donya_e_eqtesad_com(article_text_div.prettify())
                content = clean_html_withregex(content)
        
        else:
            content = None
        
        image_url = scrape_meta_url(soup)

        #eger yoxdursa body'de axtarsin
        if not image_url:
            img_div = soup.find("div", class_="full-post-image")
            if img_div:
                img_tag = img_div.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag["src"]

        if not news_shared_date:
            date_div = soup.find('div', class_='c-date')
            if date_div:
                date_text = date_div.get_text(strip=True)
                try:
                    news_shared_date = datetime.strptime(date_text, "%H:%M %d.%m.%Y")
                except ValueError:
                    news_shared_date = None
            else:
                news_shared_date = None

        return title, description, content, image_url,gallery_images, news_shared_date
    
    else:
        return None, None, None, None, None, None
