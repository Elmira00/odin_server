# rss yoxdu, https://www.nbcnews.com/latest-stories/
# region: United States
import requests
from bs4 import BeautifulSoup

from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


from utils.decorators import check_source_active


@check_source_active("https://www.nbcnews.com/")
def get_news_links_nbcnews_com(request=None):
    headers  = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    sitemap_url = "https://www.nbcnews.com/latest-stories/"
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    link_set = set()
    news_cards = soup.find_all('div', class_='wide-tease-item__wrapper df flex-column flex-row-m flex-nowrap-m enable-new-sports-feed-mobile-design')    

    for news_card in news_cards:
        news_card_body = news_card.find('div', class_='wide-tease-item__info-wrapper flex-grow-1-m')
        if news_card_body:
            all_links = news_card_body.find_all('a')
            if len(all_links) >= 2:
                second_link = all_links[1]
                href = second_link.get('href')
                if href and href not in link_set:
                    links.append(href)
                    link_set.add(href)

    for link in links[:20]:
        if "/live-blog/" in link or "live-updates" in link or "/video/" in link:
            continue
        title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_nbcnews_com(link)
        process_article_data(
            source_link="https://www.nbcnews.com/",
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


def fetch_article_details_nbcnews_com(url):
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
        news_shared_date = scrape_meta_news_shared_date(soup)
        if not news_shared_date:
            news_shared_date = soup.find("div", class_="timestamp").find("time")["datetime"] if soup.find("div", class_="timestamp") and soup.find("div", class_="timestamp").find("time") else None
        image_url = scrape_meta_url(soup)

        # figure_tag = soup.find("figure", class_="article-hero__main")
        # if figure_tag:
        #     img_tag = figure_tag.find("img")
        #     if img_tag and img_tag.get("src"):
        #         image_url = img_tag["src"]

        article_text_div = soup.find('div', class_='article-body__content')
        if article_text_div:     
            for button in article_text_div.find_all('button'):
                button.decompose() 

            for section in article_text_div.find_all('section', class_="inline-video"):
                section.decompose()
            
            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all('div', class_='html5-video-player ytp-exp-bottom-control-flexbox ytp-modern-caption ytp-livebadge-color ytp-title-enable-channel-logo ytp-fine-scrubbing-exp ytp-embed ytp-embed-playlist unstarted-mode ytp-hide-controls ytp-large-width-mode'):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None ,None,None, None
