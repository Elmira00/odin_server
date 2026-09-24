import requests
from bs4 import BeautifulSoup
import re

from dateutil import parser
import pytz

from utils.clean_content import clean_armenianweekly_com



def get_soup_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    return None


def scrape_meta_title(soup):
    tag = soup.find("meta", {"property": "og:title"})
    return tag["content"] if tag and "content" in tag.attrs else None


def scrape_meta_description(soup):
    tag = soup.find("meta", {"property": "og:description"})
    return tag["content"] if tag and "content" in tag.attrs else None


def scrape_meta_url(soup):
    tag = soup.find("meta", {"property": "og:image"})
    return tag["content"] if tag and "content" in tag.attrs else None


def scrape_meta_news_shared_date_1(soup):
    tag = soup.find("meta", {"property": "og:article:published_time"})
    if tag and "content" in tag.attrs:
        try:
            dt_utc = parser.parse(tag["content"])
            baku_tz = pytz.timezone("Asia/Baku")
            return dt_utc.astimezone(baku_tz)
        except Exception:
            return None
    return None



def scrape_meta_news_shared_date(soup):
    meta_attrs = [
        {"property": "article:published_time"},
        {"name": "article:published_time"},
        {"property": "og:updated_time"},
        {"name": "dcterms.created"},
    ]
    
    for attrs in meta_attrs:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.has_attr("content"):
            return tag["content"]
    
    return None


def scrape_clean_content(soup):
    article_div = soup.find('div', class_='post-content clearfix mb-3')
    if not article_div:
        return None

    for tag in article_div.find_all(['script', 'style','iframe','video']):
        tag.decompose()

    for img in article_div.find_all('img'):
        if img.has_attr('src'):
            new_tag = soup.new_tag('img', src=img['src'])
            img.replace_with(new_tag)
        else:
            img.decompose()

    for a in article_div.find_all('a'):
        if a.has_attr('href'):
            new_a = soup.new_tag('a', href=a['href'])
            new_a.string = a.get_text(strip=True)
            a.replace_with(new_a)
        else:
            a.decompose()

    content = clean_armenianweekly_com(article_div.prettify())

    content = re.sub(r'<div>\s*</div>', '', content)
    content = re.sub(r'<div>\s*(<div>\s*</div>\s*)+\s*</div>', '', content)
    content = re.sub(r'<div>\s*<svg[^>]*?>[\s\S]*?</svg>\s*</div>', '', content)
    content = re.sub(r'(<div>\s*){2,}(</div>\s*){2,}', '', content)
    content = re.sub(r'\n\s*\n+', '\n', content)
    content = re.sub(r'<\s*br\s*/?>', ' ', content, flags=re.IGNORECASE)
    content = re.sub(r'<\s*/?\s*o:p\s*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)

    return content



def scrape_meta_imgs(soup):
    og_image_tags = soup.find_all('meta', property='og:image')
    og_image_urls = [tag.get('content') for tag in og_image_tags if tag.get('content')]

    return og_image_urls