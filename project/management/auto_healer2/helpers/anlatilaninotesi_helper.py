

def is_anlatilaninotesi_domain():
    og_url = soup.find('meta', property='og:url')
    canonical = soup.find('link', rel='canonical')
    
    if (og_url and 'anlatilaninotesi' in og_url.get('content', '').lower()) or \
       (canonical and 'anlatilaninotesi' in canonical.get('href', '').lower()):
        return True
    return False



def find_content(soup):
    