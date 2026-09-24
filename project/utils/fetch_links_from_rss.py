
from bs4 import BeautifulSoup
import requests


def fetch_links_from_rss(rss_url, links_count):
    headers =  {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    response = requests.get(rss_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        links = [item.find('link').text for item in items if item.find('link')]
        return links[:links_count]
    else:
        return None
    
    

 