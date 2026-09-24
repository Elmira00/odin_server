import requests
from bs4 import BeautifulSoup

from datetime import datetime



headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

sitemap_url = "https://melliun.org/feed"
response = requests.get(sitemap_url, headers=headers)


if response.status_code == 200:
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        links = []
        for item in items:
            link = item.find('link').text.strip() if item.find('link') else None

            if link:
        
               
                links.append(link)
                
                
print(links)