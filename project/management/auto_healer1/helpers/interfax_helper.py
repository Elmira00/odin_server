def is_interfax_domain(soup):
    og_url = soup.find('meta', property='og:url')
    canonical = soup.find('link', rel='canonical')
    
    if (og_url and 'interfax' in og_url.get('content', '').lower()) or \
       (canonical and 'interfax' in canonical.get('href', '').lower()):
        return True
    return False

def get_interfax_media_candidates(soup):
    raw_candidates = []
    h1_tags = soup.find_all('h1')
    second_h1 = h1_tags[1] if len(h1_tags) > 1 else None
    
    if h1_tags:
        current = h1_tags[0].next_element
        while current:
            if second_h1 and current == second_h1:
                break
            if hasattr(current, 'name') and current.name in ['h2', 'h3']:
                break
                
            if hasattr(current, 'name'):
                if current.name in ['img', 'video', 'iframe', 'embed-content']:
                    if current not in raw_candidates:
                        raw_candidates.append(current)
                elif current.name == 'div':
                    classes = " ".join(current.get('class', [])).lower() if current.get('class') else ""
                    if any(v in classes for v in ['primis', 'player', 'eplayer']):
                        if current not in raw_candidates:
                            raw_candidates.append(current)
                            
            current = current.next_element
            
    return raw_candidates