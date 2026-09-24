def is_mamul_domain(soup):
    meta_url = soup.find('meta', property='og:url')
    if meta_url and 'mamul' in meta_url.get('content', '').lower():
        return True
        
    meta_site = soup.find('meta', property='og:site_name')
    if meta_site and 'mamul' in meta_site.get('content', '').lower():
        return True
        
    canonical = soup.find('link', rel='canonical')
    if canonical and 'mamul' in canonical.get('href', '').lower():
        return True
        
    return False



def get_mamul_title(soup):
        header_tag = target_container.find('header')
        h2_tag = soup.find('h2')
        if h2_tag: return h2_tag
        
        heading_divs = soup.find_all(['div', 'span', 'header'], class_=lambda x: x and any(v in x.lower() for v in ['title', 'headline', 'heading']))
        if not heading_divs: return None

        for element in heading_divs:
            if element.find_parent(['head', 'noscript', 'aside', 'nav', 'footer']): continue
            if element.find_parent(class_=lambda x: x and any(c in x.lower() for c in ['sidebar', 'right-column', 'widgets'])): continue
            classes = ' '.join(element.get('class', [])).lower()
            if any(w in classes for w in ['uptitle', 'subtitle', 'descr', 'meta', 'date']): continue
            return element
        return None

