import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import pytz



headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}


#burdaki linki deyiseceksiz
sitemap_url = "https://www.alsumaria.tv/Entertainment-News/541975/sports/%D9%85%D8%A7-%D8%AD%D9%82%D9%8A%D9%82%D8%A9-%D8%A7%D9%86%D8%AA%D9%82%D8%A7%D9%84-%D8%A8%D9%86%D8%B2%D9%8A%D9%85%D8%A7-%D8%A7%D9%84%D9%89-%D8%A8%D9%86%D9%81%D9%8A%D9%83%D8%A7-%D8%9F-%D9%85%D9%88%D8%B1%D9%8A%D9%86%D9%8A%D9%88-%D9%8A%D8%AC%D9%8A%D8%A8?src=rss&utm_source=thewall360&utm_medium=rss-articles&utm_campaign=rss&utm_term=Rss"


response = requests.get(sitemap_url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    itemprop_div = soup.find('div', class_='LongDesc')
    if itemprop_div:
        content = itemprop_div.prettify()
        print("Content:", content)
    


    
    
    # content_div = soup.find('div', class_='w-full prose dark:prose-invert prose-base prose-slate prose-a:text-blue-600 prose-blockquote:relative prose-blockquote:my-14 prose-blockquote:border-0 prose-blockquote:pl-6 prose-blockquote:font-heading prose-blockquote:text-lg prose-blockquote:italic prose-figcaption:text-sm prose-figcaption:text-slate-400 prose-strong:leading-[unset] mt-7')

    # if content_div:
    #     content = content_div.prettify()
    #     print("Content:", content)


    # meta_tag_time = soup.find("meta", {"property": "article:published_time"})
    # if meta_tag_time:
    #     date_str = meta_tag_time["content"]
    #     dt = parser.parse(date_str)  
    #     news_shared_date = dt.astimezone(pytz.UTC)
    #     print("News Shared Date:", news_shared_date)