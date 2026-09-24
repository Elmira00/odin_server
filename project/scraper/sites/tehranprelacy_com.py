# rss: https://www.tehranprelacy.com/?format=feed&type=rss
# region: Iran
from bs4 import BeautifulSoup
import requests
from scraper.models import Source
from utils.clean_content import clean_html_withregex,clean_soup_tags,clean_donya_e_eqtesad_com,extract_gallery_images
from utils.scrape_content_metatag import scrape_meta_title,scrape_meta_description,scrape_meta_url,scrape_meta_news_shared_date
from utils.process_article import process_article_data
from datetime import datetime
from django.utils import timezone

ARMENIAN_MONTHS = {
    'Հունվարի': '01', 'Փետրվարի': '02', 'Մարտի': '03', 'Ապրիլի': '04',
    'Մայիսի': '05', 'Հունիսի': '06', 'Յունիսի': '06',  # alt spelling
    'Հուլիսի': '07', 'Յուլիսի': '07',
    'Օգոստոսի': '08', 'Սեպտեմբերի': '09', 'Հոկտեմբերի': '10',
    'Նոյեմբերի': '11', 'Դեկտեմբերի': '12'
}

def convert_armenian_date_to_datetime(soup: BeautifulSoup):
    try:
        date_span = soup.find('span', class_='pre-postdateicon')
        if not date_span:
            return None

        text = date_span.get_text(strip=True)
        text = text.replace('Հրատարակւած՝ ', '').replace('ժ. ', '')
        parts = [p.strip() for p in text.split(',')][-3:]
        if len(parts) != 3:
            return None

        month_day, year, time = parts
        month_name, day = month_day.split()
        month = ARMENIAN_MONTHS.get(month_name)
        if not month:
            return None

        date_str = f"{year}-{month}-{day} {time}"
        naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return timezone.make_aware(naive, timezone.get_current_timezone())

    except Exception as e:
        print(f"Error: {e}")
        return None

from utils.decorators import check_source_active


@check_source_active("https://www.tehranprelacy.com/")
def get_news_links_tehranprelacy_com(request=None):
    sitemap_url = Source.objects.get(link="https://www.tehranprelacy.com/").rss_link
    headers = {
        "User-Agent": "Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    response = requests.get(sitemap_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        links = []
        link_set = set()

        for item in items:
            link = item.find("link").text.strip() if item.find("link") else None

            if link:
                if link not in link_set:
                    links.append((link))
                    link_set.add(link)

        for link in links[:30]:
            title, description, content, image_url, gallery_images, news_shared_date = fetch_article_details_tehranprelacy_com(link)

            process_article_data(
                source_link="https://www.tehranprelacy.com/",
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


def fetch_article_details_tehranprelacy_com(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=15)
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
        description = scrape_meta_description(soup)
        image_url = scrape_meta_url(soup)
        news_shared_date = convert_armenian_date_to_datetime(soup)

        # content

        article_text_div = soup.find("div", {'class': 'pre-article'})

        if article_text_div:

            gallery_images = extract_gallery_images(article_text_div)
            gallery_images = ['https://www.tehranprelacy.com' + img for img in gallery_images]

            for ul_class in article_text_div.find_all("ul", class_="gallery_attach_list"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("ul", class_="sigProContainer"):
                ul_class.decompose()

            for ul_class in article_text_div.find_all("div", class_="sigProPrintMessage"):
                ul_class.decompose()

            clean_soup_tags(soup, article_text_div)
            content = clean_donya_e_eqtesad_com(article_text_div.prettify())
            content = clean_html_withregex(content)
        else:
            content = None

        return title, description, content, image_url, gallery_images, news_shared_date
    else:
        return None, None, None, None, None, None
