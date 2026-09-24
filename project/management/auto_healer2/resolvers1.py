import re
import json
from collections import Counter
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from management.auto_healer.helpers.interfax_helper import is_interfax_domain, get_interfax_media_candidates
from management.auto_healer.helpers.mathrubhumi_helper import is_mathrubhumi_domain, get_mathrubhumi_media_candidates, clean_mathrubhumi_noise
from management.auto_healer.helpers.mamul_helper import is_mamul_domain
class BaseAutoHealer:
    def __init__(self, source_id, test_urls, shared_soups):
        self.source_id = source_id
        self.test_urls = test_urls
        self.shared_soups = shared_soups

    def clean_noise_from_html(self, soup):
        if getattr(soup, '_is_cleaned', False):
            return

        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'svg', 'button']):
            tag.decompose()
            
        junk_keywords = re.compile(r'(footer|sidebar|menu|comment|popup|sponsor|advert|widget|share|timeline|related|recommend|ticker|banner|sondakika|breaking|alert|marquee)', re.IGNORECASE)
        
        for tag in soup.find_all(True):
            if tag.attrs is None:
                continue
                
            css_classes = " ".join(tag.get('class', [])).lower()
            tag_id = tag.get('id', '').lower()
            
            if junk_keywords.search(css_classes) or junk_keywords.search(tag_id):
                if tag.find('article'):
                    continue
                
                if tag.find(class_=re.compile(r'article-body|post-content|entry-content|main-content', re.I)):
                    continue
                    
                if len(tag.find_all('p')) > 3 or len(tag.get_text(strip=True)) > 400:
                    continue
                
                tag.decompose()
        
        soup._is_cleaned = True


    def check_meta_tags(self, soup, meta_mappings):
        for mapping in meta_mappings:
            meta_tag = soup.find(mapping["tag"], attrs=mapping["attrs"])
            if meta_tag:
                content = meta_tag.get("content") or meta_tag.get("href")
                if content:
                    return content, mapping 
        return None, None

    def check_json_ld(self, soup, expected_keys):
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string: 
                continue
            try:
                data = json.loads(script.string.strip())
                items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else [data]
                
                for item in items:
                    if not isinstance(item, dict): 
                        continue
                   
                    for key in expected_keys:
                        if item.get(key):
                            return key 
            except Exception:
                continue
                
        return None

    def calculate_dom_distance(self, node1, node2):
        ancestors1 = list(node1.parents)
        ancestors2 = list(node2.parents)

        if node2 in ancestors1:
            return ancestors1.index(node2)
        if node1 in ancestors2:
            return ancestors1.index(node1)

        common_ancestor = None
        for anc in ancestors1:
            if anc in ancestors2:
                common_ancestor = anc
                break

        if not common_ancestor:
            return 999 

        return ancestors1.index(common_ancestor) + ancestors2.index(common_ancestor)

    def generate_css_selector(self, target_node):
        if not target_node:
            return ""
        
        tag_name = target_node.name
        node_id = target_node.get('id')
        if node_id and isinstance(node_id, str) and not node_id.startswith("ctl"):
            return f"{tag_name}#{node_id}"

        path = []
        current = target_node
        
        while current and current.name != 'body' and current.name != '[document]':
            identifier = current.name
            
            classes = current.get('class')
            if classes:
                valid_classes = []
                for c in classes:
                    c_lower = c.lower()
                    if any(w in c_lower for w in ['active', 'lazy', 'visible']):
                        continue
                    valid_classes.append(c)

                if valid_classes:
                    identifier += f".{valid_classes[0]}"
            
            parent = current.parent
            if parent:
                siblings = [sib for sib in parent.find_all(current.name, recursive=False)]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    identifier += f":nth-of-type({index})"

            path.append(identifier)
            current = parent

        path.reverse()
        return " > ".join(path)

    def run_diagnostics(self):
        raise NotImplementedError("Subclasses must implement run_diagnostics")


class ImageAutoHealer(BaseAutoHealer):
    meta_tags = [
        {"tag": "meta", "attrs": {"property": "og:image"}},
        {"tag": "meta", "attrs": {"property": "og:image:url"}},
        {"tag": "meta", "attrs": {"property": "og:image:secure_url"}},
        {"tag": "meta", "attrs": {"name": "twitter:image"}},
        {"tag": "meta", "attrs": {"name": "twitter:image:src"}},
        {"tag": "meta", "attrs": {"itemprop": "image"}},
        {"tag": "link", "attrs": {"rel": "image_src"}},
    ]
    
    def get_h1_or_fallback(self, soup):
        h1_tag = soup.find('h1')
        if not h1_tag:
            h1_tag = soup.find(['h2', 'h3', 'div'], class_=lambda x: x and 'title' in x.lower())
        return h1_tag

    def get_all_media_candidates(self, soup):
        if is_mathrubhumi_domain(soup):
            return get_mathrubhumi_media_candidates(soup) 
            
        raw_candidates = []
        if is_interfax_domain(soup):
            raw_candidates = get_interfax_media_candidates(soup)
        else:
            basic_media = soup.find_all(['img', 'video', 'iframe', 'embed-content'])
            player_divs = soup.find_all('div', class_=lambda x: x and any(v in x.lower() for v in ['primis', 'player', 'eplayer']))
            custom_media = soup.find_all(lambda tag: tag.has_attr('media-url') or tag.has_attr('data-video') or tag.has_attr('data-src') or tag.has_attr('data-lazy'))
            
            seen = set()
            for tag in list(basic_media) + list(player_divs) + list(custom_media):
                if id(tag) not in seen:
                    seen.add(id(tag))
                    raw_candidates.append(tag)
            
        valid_candidates = []
        seen = set()
        for elem in raw_candidates:
            if id(elem) in seen: continue
            seen.add(id(elem))

            parent_has_bad_class = False
            for parent in elem.parents:
                if parent.name in ['head', 'noscript', 'aside', 'nav', 'footer']:
                    parent_has_bad_class = True
                    break
                if parent.get('class'):
                    p_classes = " ".join(parent.get('class')).lower()
                    if any(c in p_classes for c in ['sidebar', 'right-column', 'widgets', 'timeline', 'related', 'feed', 'stream', 'comments', 'recommend', 'slider', 'carousel', 'promo','podcast', 'audio', 'briefing','banner','advert', 'sponsor', 'adbox', 'insideind']):
                        parent_has_bad_class = True
                        break
            
            if parent_has_bad_class: continue
            
            src = elem.get('data-lazy') or elem.get('data-src') or elem.get('src') or elem.get('media-url') or elem.get('data-video') or elem.get('poster') or elem.get('srcset') or elem.get('id')
            if not src and elem.name == 'video':
                source_tag = elem.find('source')
                if source_tag: src = source_tag.get('src')

            if not src or len(str(src)) < 5: continue

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
                        if int(width) < 50 or int(height) < 50: continue
                    except ValueError: pass
                
                meta_str = f"{elem.get('id', '')} {' '.join(elem.get('class', []))} {src_lower}".lower()
                # if any(w in meta_str for w in ['icon', 'logo', 'avatar', 'pixel', 'spacer', 'ads', 'author', 'yazar']):
                #     continue
                if re.search(r'\b(icon|logo|avatar|pixel|spacer|ads|author|yazar)\b', meta_str):
                    continue


            valid_candidates.append(elem)
        return valid_candidates

    def find_image_by_h1_proximity(self, soup):
        h1_tag = self.get_h1_or_fallback(soup)
        if not h1_tag: return None

        candidates = self.get_all_media_candidates(soup)
        if not candidates: return None

        best_candidate = None
        min_distance = float('inf')

        for elem in candidates:
            distance = self.calculate_dom_distance(h1_tag, elem)
            if distance < min_distance:
                min_distance = distance
                best_candidate = elem

        return best_candidate

    def find_image_by_tf_idf(self, soup):
        article_text = ""
        h1_tag = self.get_h1_or_fallback(soup)
        
        if h1_tag:
            paragraphs = h1_tag.find_all_next('p')
            article_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        else:
            paragraphs = soup.find_all('p')
            article_text = " ".join(p.get_text(strip=True) for p in paragraphs)
            
        if not article_text or len(article_text) < 50:
            article_text = h1_tag.get_text(strip=True) if h1_tag else ""
            
        if not article_text: return None
            
        candidates = self.get_all_media_candidates(soup)
        if not candidates: return None
            
        corpus = [article_text]
        tag_contexts = []
        
        for cand in candidates:
            context_text = f"{cand.get('alt', '')} {cand.get('title', '')} "
            parent = cand.parent
            if parent:
                if parent.name == 'picture' and parent.parent:
                    context_text += parent.parent.get_text(strip=True)[:250] + " "
                else:
                    context_text += parent.get_text(strip=True)[:250] + " "
            tag_contexts.append(context_text.strip() or "empty media")
            
        corpus.extend(tag_contexts)
        
        try:
            vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b').fit_transform(corpus)
            vectors = vectorizer.toarray()
            
            content_vec = vectors[0].reshape(1, -1)
            candidate_vecs = vectors[1:]
            
            similarities = cosine_similarity(content_vec, candidate_vecs)[0]
            best_idx = similarities.argmax()
            
            if similarities[best_idx] > 0.01: 
                return candidates[best_idx]
        except Exception:
            pass
            
        return None
        
    def find_image_by_heuristic_score(self, soup):
        candidates = self.get_all_media_candidates(soup)
        if not candidates: return None
            
        best_cand = None
        max_score = -1
        
        for cand in candidates:
            score = 10  
            src = str(cand.get('src') or cand.get('data-src') or cand.get('media-url') or cand.get('poster') or '')

            if any(audio_key in src.lower() for audio_key in ['spotify', 'soundcloud', 'audio', 'podcast']): continue
            if cand.name == 'iframe' and not any(k in src.lower() for k in ['youtube', 'vimeo', 't.me', 'embed', 'video', 'player']):
                score = 0
                continue
            if cand.name == 'video': score += 50
            elif cand.name in ['iframe', 'embed-content'] and any(k in src.lower() for k in ['youtube', 'vimeo', 'video', 'embed', 'player', 't.me']):
                score += 50
                
            if any(k in src.lower() for k in ['hero', 'large', 'cover', 'main', 'article', 'feature']): score += 30
                
            width = cand.get('width', '0')
            height = cand.get('height', '0')
            if str(width).isdigit() and str(height).isdigit():
                w, h = int(width), int(height)
                if w > 400: score += 20
                if w > h: score += 10
                    
            if score > max_score:
                max_score = score
                best_cand = cand
                
        return best_cand

    def run_diagnostics(self):
        generated_selectors = [] 
        total_urls = len(self.test_urls) 
        
        for index, url in enumerate(self.test_urls, 1):
            soup = self.shared_soups.get(url)
            if not soup:
                print(f"[DEBUG] ImageHealer: URL {index} failed in central fetch. Treated as invalid.")
                continue

            if is_mathrubhumi_domain(soup):
                if not getattr(soup, '_is_cleaned', False):
                    clean_mathrubhumi_noise(soup)
                    soup._is_cleaned = True
            else:
                self.clean_noise_from_html(soup)

            target_node_tfidf = self.find_image_by_tf_idf(soup)
            target_node_heur = self.find_image_by_heuristic_score(soup)
            target_node_h1 = self.find_image_by_h1_proximity(soup)

            votes = []
            if target_node_h1: votes.append(target_node_h1)
            if target_node_tfidf: votes.append(target_node_tfidf)
            if target_node_heur: votes.append(target_node_heur)

            winner_tag = None
            if votes:
                vote_counts = Counter(votes)
                most_common_tag, count = vote_counts.most_common(1)[0]
                if count >= 2:
                    winner_tag = most_common_tag
                    
            if not winner_tag:
                if target_node_heur and (target_node_heur.name in ['iframe', 'video', 'embed-content'] or target_node_heur.has_attr('media-url')):
                    winner_tag = target_node_heur
                elif target_node_heur:
                    winner_tag = target_node_heur
            
            if winner_tag:
                new_selector = self.generate_css_selector(winner_tag)
                generated_selectors.append(new_selector)

        valid_selectors = [sel for sel in generated_selectors if sel]
        
        if not valid_selectors:
            return None
            
        selector_counts = Counter(valid_selectors)
        best_selector, best_count = selector_counts.most_common(1)[0]
        
        if best_count >= 2 and (best_count / len(valid_selectors)) > 0.5:
            return {"resolution_type": "css_selector", "rule": best_selector}
        elif total_urls <= 2 and best_count == 1:
            return {"resolution_type": "css_selector", "rule": best_selector}
        else:
            return None


class SharedDateAutoHealer(BaseAutoHealer):
    def __init__(self, source_id, test_urls, shared_soups):
        super().__init__(source_id, test_urls, shared_soups)
        self.meta_tags = [
            {"tag": "meta", "attrs": {"property": "article:published_time"}},
            {"tag": "meta", "attrs": {"property": "article:modified_time"}},
            {"tag": "meta", "attrs": {"name": "pubdate"}},
            {"tag": "meta", "attrs": {"name": "publishdate"}},
            {"tag": "meta", "attrs": {"name": "timestamp"}},
            {"tag": "meta", "attrs": {"name": "dc.date.issued"}},
            {"tag": "meta", "attrs": {"property": "og:pubdate"}},
        ]

    def check_json_ld_date(self, soup):
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string: continue
            try:
                data = json.loads(script.string.strip())
                items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else [data]
                for item in items:
                    if not isinstance(item, dict): continue
                    if item.get("datePublished") or item.get("dateModified") or item.get("uploadDate"): return True
            except Exception: continue
        return False

    def is_valid_date_format(self, text):
        if not text: return False
        numeric_pattern = re.compile(r'\b(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]20\d{2})\b')
        if numeric_pattern.search(text): return True
        textual_pattern = re.compile(r'\b\d{1,2}\s+[a-zA-Zа-яА-ЯəşçğıöüƏŞÇĞIÖÜ]+\s+20\d{2}\b', re.IGNORECASE)
        if textual_pattern.search(text): return True

        return False

    def find_date_node(self, soup):
        for tag in soup.find_all('time'):
            if tag.has_attr('datetime') or self.is_valid_date_format(tag.get_text()): return tag
        itemprop_tags = soup.find_all(attrs={"itemprop": re.compile(r'datePublished|dateModified|uploadDate', re.I)})
        if itemprop_tags: return itemprop_tags[0]
        date_keywords = ['date', 'time', 'pubdate', 'timestamp', 'post-meta', 'article-date', 'yayin-tarihi', 'saat']
        for tag in soup.find_all(['span', 'div', 'p', 'li']):
            class_str = " ".join(tag.get('class', [])).lower()
            id_str = tag.get('id', '').lower()
            if any(kw in class_str or kw in id_str for kw in date_keywords):
                if self.is_valid_date_format(tag.get_text()): return tag
        return None

    def run_diagnostics(self):
        generated_selectors = []
        url_patterns = []
        total_urls = len(self.test_urls) 

        for index, url in enumerate(self.test_urls, 1):
            soup = self.shared_soups.get(url)
            if not soup:
                continue

            self.clean_noise_from_html(soup)

            date_node = self.find_date_node(soup)
            if date_node:
                selector = self.generate_css_selector(date_node)                
                generated_selectors.append(selector)
            else:
                url_date_match = re.search(r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2})', url)
                if url_date_match:
                    url_patterns.append(r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2})')

        if generated_selectors:
            selector_counts = Counter(generated_selectors)
            best_selector, best_count = selector_counts.most_common(1)[0]
            
            if best_count >= 2 and (best_count / len(generated_selectors)) > 0.5:
                return {"resolution_type": "css_selector", "rule": best_selector}
            elif len(generated_selectors) == 1 and total_urls <= 2:
                return {"resolution_type": "css_selector", "rule": best_selector}

        if url_patterns:
            pattern_counts = Counter(url_patterns)
            best_pattern, best_count = pattern_counts.most_common(1)[0]
            
            if best_count >= 2 or (total_urls == 1 and best_count == 1):
                return {"resolution_type": "url_regex", "rule": best_pattern}

        return None


class TitleAutoHealer(BaseAutoHealer):
    def __init__(self, source_id, test_urls, shared_soups):
        super().__init__(source_id, test_urls, shared_soups)
        self.meta_tags = [
            {"tag": "meta", "attrs": {"property": "og:title"}},
            {"tag": "meta", "attrs": {"name": "twitter:title"}},
            {"tag": "meta", "attrs": {"itemprop": "name"}},
            {"tag": "meta", "attrs": {"itemprop": "headline"}},
            {"tag": "meta", "attrs": {"name": "apple-mobile-web-app-title"}},
            {"tag": "meta", "attrs": {"name": "application-name"}},
        ]

    def find_title(self, soup):
        article_tag = soup.find('article')
        target_container = article_tag if article_tag else soup
        # if is_mamul_domain:
        #     get_mamul_title(soup)
        #     continue
        header_tag = target_container.find('header')
        if header_tag:
            h1_in_header = header_tag.find('h1')
            if h1_in_header: return h1_in_header

        h1_tag = soup.find('h1')
        if h1_tag: return h1_tag

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

    def run_diagnostics(self):
        generated_selectors = []
        total_urls = len(self.test_urls)
        
        for index, url in enumerate(self.test_urls, 1):
            soup = self.shared_soups.get(url)
            if not soup:
                continue

            self.clean_noise_from_html(soup)

            target_node = self.find_title(soup)
            if target_node:
                new_selector = self.generate_css_selector(target_node)
                if new_selector: 
                    generated_selectors.append(new_selector)

        if generated_selectors:
            selector_counts = Counter(generated_selectors)
            best_selector, best_count = selector_counts.most_common(1)[0]
            
            if best_count >= 2 or (total_urls == 1 and best_count == 1):
                return {"resolution_type": "css_selector", "rule": best_selector}
        return None


class DescriptionAutoHealer(BaseAutoHealer):
    def __init__(self, source_id, test_urls, shared_soups):
        super().__init__(source_id, test_urls, shared_soups)
        self.meta_tags = [
            {"tag": "meta", "attrs": {"property": "og:description"}},
            {"tag": "meta", "attrs": {"name": "description"}},
            {"tag": "meta", "attrs": {"property": "twitter:description"}},
            {"tag": "meta", "attrs": {"itemprop": "description"}}
        ]

    def find_description(self, soup):
        desc_classes = ['lead', 'summary', 'excerpt', 'description', 'subtitle']
        desc_elements = soup.find_all(['div', 'p', 'span', 'h2', 'h3'], class_=lambda x: x and any(v in str(x).lower() for v in desc_classes))
        
        if desc_elements:
            for element in desc_elements:
                if element.find_parent(['nav', 'footer', 'aside', 'header']): continue
                if element.text and len(element.text.strip()) > 15: return element

        hgroups = soup.find_all('hgroup')
        for hgroup in hgroups:
            p_in_hgroup = hgroup.find(['p', 'h2', 'h3'])
            if p_in_hgroup and len(p_in_hgroup.text.strip()) > 15: return p_in_hgroup

        article_body = soup.find(['article', 'main']) or soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
        if article_body:
            paragraphs = article_body.find_all('p')
            for p in paragraphs:
                if p.text and len(p.text.strip()) > 30: return p
        return None

    def run_diagnostics(self):
        generated_selectors = []
        total_urls = len(self.test_urls)
        
        for index, url in enumerate(self.test_urls, 1):
            soup = self.shared_soups.get(url)
            if not soup:
                continue

            self.clean_noise_from_html(soup)

            meta_value, successful_mapping = self.check_meta_tags(soup, self.meta_tags)
            if meta_value and len(meta_value.strip()) > 5:
                return {"resolution_type": "meta", "rule": successful_mapping}

            target_node = self.find_description(soup)
            if target_node:
                new_selector = self.generate_css_selector(target_node)
                if new_selector and new_selector.count('nth-of-type') <= 2:
                    generated_selectors.append(new_selector)

        if generated_selectors:
            selector_counts = Counter(generated_selectors)
            best_selector, best_count = selector_counts.most_common(1)[0]
            
            if best_count >= 2 or (total_urls == 1 and best_count == 1):
                return {"resolution_type": "css_selector", "rule": best_selector}
        return None


class ContentAutoHealer(BaseAutoHealer):
    def __init__(self, source_id, test_urls, shared_soups):
        super().__init__(source_id, test_urls, shared_soups)

    def find_content(self, soup):
        data_target = soup.find(attrs={"data-article-body": "true"}) or soup.find(attrs={"data-body-type": "bodyblocks"})
        if data_target:
            if not data_target.find_parent(['nav', 'footer', 'aside', 'header']): return data_target
            
        h1_tag = soup.find('h1')
        search_scope = soup
        if h1_tag:
            parent_article = h1_tag.find_parent(['article', 'main', 'div','section'])
            if parent_article: search_scope = parent_article

        content_pattern = re.compile(r'content-inner|article-body|post-content|entry-content|story-body|article-text|page-content|main-content|article_content|content', re.IGNORECASE)
        content_elements = search_scope.find_all(['div', 'article', 'section'], class_=content_pattern)
        
        if content_elements:
            content_elements.reverse()
            for element in content_elements:
                if element.find_parent(['nav', 'footer', 'aside', 'header']): continue
                element_classes = " ".join(element.get('class', [])).lower()
                parent_classes = " ".join([str(p.get('class', '')) for p in element.parents]).lower()
                bad_words = ['overlay', 'popup', 'modal', 'cookie', 'banner', 'newsletter']
                if any(bw in element_classes or bw in parent_classes for bw in bad_words): continue

                paragraphs = element.find_all('p')
                if len(paragraphs) >= 2 or len(element.text.strip()) > 200: return element

        semantic_elements = search_scope.find_all(['article', 'main'])
        if semantic_elements:
            semantic_elements.reverse()
            for element in semantic_elements:
                paragraphs = element.find_all('p')
                if len(paragraphs) >= 2 or len(element.text.strip()) > 200: return element

        all_divs = search_scope.find_all(['div', 'section'])
        max_p_count = 0
        best_block = None
        
        for div in all_divs:
            if div.find_parent(['nav', 'footer', 'aside', 'header']): continue
            p_count = len(div.find_all('p', recursive=False)) 
            if p_count > max_p_count:
                max_p_count = p_count
                best_block = div

        if best_block and max_p_count >= 2: return best_block
        return None

    def run_diagnostics(self):
        generated_selectors = []
        total_urls = len(self.test_urls)
        
        for index, url in enumerate(self.test_urls, 1):
            soup = self.shared_soups.get(url)
            if not soup:
                continue

            self.clean_noise_from_html(soup)

            target_node = self.find_content(soup)
            if target_node:
                new_selector = self.generate_css_selector(target_node)
                generated_selectors.append(new_selector)

        if generated_selectors:
            selector_counts = Counter(generated_selectors)
            best_selector, best_count = selector_counts.most_common(1)[0]
            
            if best_count >= 2 or (total_urls == 1 and best_count == 1):
                return {"resolution_type": "css_selector", "rule": best_selector}
        return None