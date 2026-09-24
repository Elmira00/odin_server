# rss: https://www.iran-emrooz.net/index.php/home/rss/
# iran

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data


def get_news_links_iran_emrooz_net(request=None):
    sitemap_url = Source.objects.get(link="https://www.iran-emrooz.net/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None
            pub_date_raw = item.find('dc:date').text.strip() if item.find('dc:date') else None 
            descriptions = item.find_all("description")
            content = descriptions[1].get_text(strip=True) if len(descriptions) > 1 else (descriptions[0].get_text(strip=True) if descriptions else None)

            if link and pub_date_raw and content:
                if link not in link_set:
                    dt = pub_date_raw
                    
                    links.append((link, dt, content))
                    link_set.add(link)

        for link, news_shared_date, content in links[:20]:
            title, description, image_url, gallery_images = fetch_article_details_iran_emrooz_net(link)

            process_article_data(
                source_link="https://www.iran-emrooz.net/",
                link=link,
                title=title,
                description=description,
                content=content,
                image_url=image_url,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date,
            )
    else:
        None


def fetch_article_details_iran_emrooz_net(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8"

    title = None
    description = None
    content = None
    gallery_images = []
    image_url = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find('title').get_text(strip=True)
        description = scrape_meta_description(soup)
        if not description:
            description = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None

        image_url = soup.find('div', {'class': 'boxbody'}).find('img')['src'] if soup.find('div', {'class': 'boxbody'}) and soup.find('div', {'class': 'boxbody'}).find('img') else None

        # content

        article_text_div = soup.find('h4')

        if article_text_div:

            CLASS_MATCHES = {
                "div": ['news_controll']
            }
            for tag_name, class_list in CLASS_MATCHES.items():
                for class_name in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=class_name):
                        tag.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", 'svg']):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, image_url, gallery_images
    else:
        return None, None, None, None