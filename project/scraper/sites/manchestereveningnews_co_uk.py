# # rss: https://www.manchestereveningnews.co.uk/news/?service=rss
# # region: UK

# import re

# from bs4 import BeautifulSoup
# import requests
# from scraper.models import Source
# from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
# from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
# from utils.process_article import process_article_data

# from utils.decorators import check_source_active


# @check_source_active("https://www.manchestereveningnews.co.uk/")
# def get_news_links_manchestereveningnews_co_uk(request=None):
#     sitemap_url = Source.objects.get(link="https://www.manchestereveningnews.co.uk/").rss_link
#     headers = {
#         "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
#     }
#     response = requests.get(sitemap_url, headers=headers, timeout=10)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, "xml")
#         items = soup.find_all("item")

#         links = []
#         link_set = set()

#         for item in items:
#             link = item.find("link").text.strip() if item.find("link") else None
#             if "-live-" in link:
#                 continue
#             if "/gallery/" in link:
#                 continue
#             rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

#             if link and rss_image:
#                 if link not in link_set:
#                     links.append((link, rss_image))
#                     link_set.add(link)

#         for link, rss_image in links[:25]:
#             title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_manchestereveningnews_co_uk(link)
#             if not image_url:
#                 image_url = rss_image
#             process_article_data(
#                 source_link="https://www.manchestereveningnews.co.uk/",
#                 link=link,
#                 title=title,
#                 description=description,
#                 content=content,
#                 image_url=image_url,
#                 gallery_images=gallery_images,
#                 news_shared_date=news_shared_date,
#             )
#     else:
#         None


# def fetch_article_details_manchestereveningnews_co_uk(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers, timeout=10)
#     response.encoding = "utf-8"

#     title = None
#     description = None
#     content = None
#     gallery_images = []
#     image_url = None
#     news_shared_date = None

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         if soup.find("div", class_=re.compile(r"LiveEvents_wrapper*")):
#             return None, None, None, None, None, None

#         title = scrape_meta_title(soup)
#         description = scrape_meta_description(soup)
#         image_url = scrape_meta_url(soup)
#         news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content'] if soup.find('meta', {'property': 'article:published_time'}) else None

#         # content

#         article_text_div = soup.find("article", {'class': 'ArticleBody_article__AwrJE'})
#         if not article_text_div:
#             article_text_div = soup.find("div", {"class": re.compile(r'NeedToKnowTemplate_inner-wrapper*')})
            
#         if not article_text_div:

#         if article_text_div:

#             CLASS_MATCHES = {
#                 "div": ["Byline_byline-container__K_Owl", 'BoxStyles_box-container__Qk3WH',
#                         'HtmlEmbed_container__x6svQ', 'YoutubeEmbed_video-wrapper__flGzW'],
#                 'section': ['Grid_grid-container__uDzQC', "SocialFollowBar_wrapper__h4k_D"],
#                 'aside': ['Factbox_factbox-container__hSMOa'],
#                 'strong': ['Strong_strong__e2x35']
#             }
#             for tag_name, class_list in CLASS_MATCHES.items():
#                 for class_name in class_list:
#                     for tag in soup.find_all(tag_name, class_=class_name):
#                         tag.decompose()

#             CLASS_MATCHES = {
#                 "div": ["ImageEmbed_image-embed__0T8WX"],
#             }
#             for tag_name, class_list in CLASS_MATCHES.items():
#                 for class_name in class_list:
#                     for tag in soup.find_all(tag_name, class_=class_name):
#                         tag.decompose()

#             for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
#                 ul_class.decompose()

#             for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "a", 'h1', 'h2', 'span', "nav"]):
#                 ul_class.decompose()

#             gallery_images = extract_gallery_images(article_text_div)

#             clean_soup_tags(soup, article_text_div)
#             content = clean_donya_e_eqtesad_com(article_text_div.prettify())
#             content = clean_html_withregex(content)
#         else:
#             content = None

#         return title, description, content, image_url, gallery_images, news_shared_date
#     else:
#         return None, None, None, None, None, None























# rss: https://www.manchestereveningnews.co.uk/news/?service=rss
# region: UK

import re

from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data

from utils.decorators import check_source_active


@check_source_active("https://www.manchestereveningnews.co.uk/")
def get_news_links_manchestereveningnews_co_uk(request=None):
    sitemap_url = Source.objects.get(link="https://www.manchestereveningnews.co.uk/").rss_link
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
            if "-live-" in link:
                continue
            if "/gallery/" in link:
                continue
            rss_image = item.find("enclosure")["url"].strip() if item.find("enclosure") and item.find("enclosure").get("url") else None

            if link and rss_image:
                if link not in link_set:
                    links.append((link, rss_image))
                    link_set.add(link)

        for link, rss_image in links[:25]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_manchestereveningnews_co_uk(link)
            if not image_url:
                image_url = rss_image
            process_article_data(
                source_link="https://www.manchestereveningnews.co.uk/",
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


def fetch_article_details_manchestereveningnews_co_uk(url):
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
    news_shared_date = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        title = scrape_meta_title(soup)
        if not title:
            title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        news_shared_date = soup.find('meta', {'property': 'article:published_time'})['content'] if soup.find('meta', {'property': 'article:published_time'}) else None

      
        article_text_div = None
        
        # 1.Yeni React şablonu (ex: ArticleBody_article__AwrJE)
        if not article_text_div:
            article_text_div = soup.find("article", class_=re.compile(r'^ArticleBody_article__.*'))
            
        # 2.Live Events şablonu 
        if not article_text_div:
            article_text_div = soup.find("article", class_=re.compile(r'^LiveEvents_article-body__.*'))
            
        # 3.Klassik Şablon 
        if not article_text_div:
            article_text_div = soup.find("div", class_="article-body")
            
        # 4."Need to know" şablonu 
        if not article_text_div:
            article_text_div = soup.find("div", class_=re.compile(r'^NeedToKnowTemplate_inner-wrapper.*'))


        if article_text_div:
            CLASS_MATCHES = {
                "div": ["Byline_byline-container", "BoxStyles_box-container",
                        "HtmlEmbed_container", "YoutubeEmbed_video-wrapper", 
                        "ImageEmbed_image-embed", "UpdateButton_wrapper"], 
                "section": ["Grid_grid-container", "SocialFollowBar_wrapper"],
                "aside": ["Factbox_factbox-container"],
                "strong": ["Strong_strong"]
            }
            
            for tag_name, class_list in CLASS_MATCHES.items():
                for base_class in class_list:
                    for tag in article_text_div.find_all(tag_name, class_=re.compile(f'^{base_class}.*')):
                        tag.decompose()

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all(["figure", "script", "iframe", "aside", "a", 'h1', 'h2', 'span', "nav", "header"]):
                ul_class.decompose()

            gallery_images = extract_gallery_images(article_text_div)

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None