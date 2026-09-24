import re


def is_mathrubhumi_domain(soup):
    meta_url = soup.find('meta', property='og:url')
    if meta_url and 'mathrubhumi' in meta_url.get('content', '').lower():
        return True
        
    meta_site = soup.find('meta', property='og:site_name')
    if meta_site and 'mathrubhumi' in meta_site.get('content', '').lower():
        return True
        
    canonical = soup.find('link', rel='canonical')
    if canonical and 'mathrubhumi' in canonical.get('href', '').lower():
        return True
        
    return False



def clean_mathrubhumi_noise(soup):
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'svg', 'button']):
        tag.decompose()
        
    junk_keywords = re.compile(r'(footer|menu|comment|popup|sponsor|advert|widget|share|timeline|related|recommend)', re.IGNORECASE)
    
    for tag in soup.find_all(True):
        if tag.attrs is None:
            continue
            
        css_classes = " ".join(tag.get('class', []))
        tag_id = tag.get('id', '')
        
        if junk_keywords.search(css_classes) or junk_keywords.search(tag_id):
            tag.decompose()


def get_mathrubhumi_media_candidates(soup):
    basic_media = soup.find_all(['img', 'video', 'iframe', 'embed-content'])
    player_divs = soup.find_all('div', class_=lambda x: x and any(v in x.lower() for v in ['primis', 'player', 'eplayer']))
    custom_media = soup.find_all(lambda tag: tag.has_attr('media-url') or tag.has_attr('data-video') or tag.has_attr('data-src') or tag.has_attr('data-lazy'))
    
    seen_ids = set()
    raw_candidates = []
    for tag in list(basic_media) + list(player_divs) + list(custom_media):
        if id(tag) not in seen_ids:
            seen_ids.add(id(tag))
            raw_candidates.append(tag)

    valid_candidates = []
    
    for elem in raw_candidates:
        parent_has_bad_class = False
        for parent in elem.parents:
            if parent.name in ['head', 'noscript', 'aside', 'nav', 'footer']:
                parent_has_bad_class = True
                break
            if parent.get('class'):
                p_classes = " ".join(parent.get('class')).lower()
                if any(c in p_classes for c in ['right-column', 'widgets', 'timeline',
                 'related', 'feed', 'stream', 'comments', 'recommend', 'slider', 'carousel', 
                 'promo','podcast', 'audio', 'briefing','blocker','advert', 'sponsor', 'adbox', 'insideind']):
                    parent_has_bad_class = True
                    break
        
        if parent_has_bad_class:
            continue

        src = elem.get('data-lazy') or elem.get('data-src') or elem.get('src') or elem.get('media-url') or elem.get('data-video') or elem.get('poster') or elem.get('srcset') or elem.get('id')
        
        if not src and elem.name == 'video':
            source_tag = elem.find('source')
            if source_tag:
                src = source_tag.get('src')

        if not src or len(str(src)) < 5:
            continue

        src_lower = str(src).lower()
        if any(audio_key in src_lower for audio_key in ['spotify', 'soundcloud', 'audio', 'podcast', 'listen']):
            continue

        if elem.name == 'img':
            if any(w in src_lower for w in ['no-image', 'placeholder', 'author', 'yazar', 'avatar', 'profile']):
                continue

            width = elem.get('width')
            height = elem.get('height')
            if width and height:
                try:
                    if int(width) < 50 or int(height) < 50:
                        continue
                except ValueError:
                    pass
            
            meta_str = f"{elem.get('id', '')} {' '.join(elem.get('class', []))} {src_lower}".lower()
            if any(w in meta_str for w in ['icon', 'logo', 'avatar', 'pixel', 'spacer', 'ads', 'author', 'yazar']):
                continue

        valid_candidates.append(elem)

    return valid_candidates