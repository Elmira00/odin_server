#project/management/auto_healer/resolvers.py

import re
import json
from collections import Counter
from datetime import datetime
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from management.auto_healer.helpers.interfax_helper import is_interfax_domain, get_interfax_media_candidates
from management.auto_healer.helpers.mathrubhumi_helper import is_mathrubhumi_domain, get_mathrubhumi_media_candidates, clean_mathrubhumi_noise
from management.auto_healer.helpers.mamul_helper import is_mamul_domain
from management.auto_healer.helpers.formulanews_helper import get_formulanews_date_candidate
from management.auto_healer.helpers.lentaz_helper import get_lentaz_date_candidate

#project/management/auto_healer/resolvers.py
class BaseAutoHealer:
    def __init__(self, source_id, test_urls, shared_soups):
        self.source_id = source_id
        self.test_urls = test_urls
        self.shared_soups = shared_soups

    # ------------------------------------------------------------------
    # Shared prep
    # ------------------------------------------------------------------

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

    def iter_cleaned_soups(self):
        """Yield (url, soup) pairs, applying domain-specific + generic cleaning once per soup."""
        for url in self.test_urls:
            soup = self.shared_soups.get(url)
            if not soup:
                continue

            if is_mathrubhumi_domain(soup):
                if not getattr(soup, '_is_cleaned', False):
                    clean_mathrubhumi_noise(soup)
                    soup._is_cleaned = True
            else:
                self.clean_noise_from_html(soup)

            yield url, soup

    # ------------------------------------------------------------------
    # Structured-data lookups (highest priority, cheapest, most reliable)
    # ------------------------------------------------------------------

    def get_json_ld_items(self, soup):
        """Return a flat list of dict items parsed out of every JSON-LD block on the page."""
        items = []
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
            except Exception:
                continue

            candidates = data if isinstance(data, list) else [data]
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                if isinstance(candidate.get("@graph"), list):
                    items.extend(x for x in candidate["@graph"] if isinstance(x, dict))
                else:
                    items.append(candidate)
        return items

    def get_json_ld_value(self, soup, keys):
        """Return the first non-empty value found in JSON-LD for any of the given keys,
        preferring items typed as Article/NewsArticle/BlogPosting when present."""
        items = self.get_json_ld_items(soup)
        if not items:
            return None

        def type_matches(item):
            t = item.get("@type")
            if isinstance(t, list):
                t = " ".join(str(x) for x in t)
            t = str(t or "").lower()
            return any(k in t for k in ("article", "newsarticle", "blogposting", "webpage"))

        ordered = [i for i in items if type_matches(i)] + [i for i in items if not type_matches(i)]

        for item in ordered:
            for key in keys:
                val = item.get(key)
                if not val:
                    continue
                if isinstance(val, dict):
                    val = val.get("url") or val.get("@id") or val.get("name")
                if isinstance(val, list):
                    val = next((v for v in val if v), None)
                    if isinstance(val, dict):
                        val = val.get("url") or val.get("@id")
                if val:
                    return str(val).strip()
        return None

    def check_json_ld(self, soup, expected_keys):
        """Legacy helper kept for compatibility: returns just the matched key name."""
        items = self.get_json_ld_items(soup)
        for item in items:
            for key in expected_keys:
                if item.get(key):
                    return key
        return None

    def check_meta_tags(self, soup, meta_mappings):
        for mapping in meta_mappings:
            meta_tag = soup.find(mapping["tag"], attrs=mapping["attrs"])
            if meta_tag:
                content = meta_tag.get("content") or meta_tag.get("href")
                if content:
                    return content, mapping
        return None, None

    def resolve_from_value_tier(self, soups, getter, min_len=1):
        """Check a cheap value-based tier (meta tag or JSON-LD) across every
        fetched soup and only commit to it if a real majority of sample pages
        actually have it -- a single sample URL having e.g. datePublished
        while most of the source's normal articles don't would otherwise
        silently poison the resolution rule for every future page. Mirrors
        the same consensus policy used for DOM-selector voting.
        getter(soup) -> (value, rule) or (None, None).
        """
        soups = list(soups)
        if not soups:
            return None

        hits = 0
        first_rule = None
        for soup in soups:
            value, rule = getter(soup)
            if value and len(str(value).strip()) >= min_len:
                hits += 1
                if first_rule is None:
                    first_rule = rule

        if len(soups) == 1:
            return first_rule if hits == 1 else None

        if hits / len(soups) > 0.5:
            return first_rule

        return None

    # ------------------------------------------------------------------
    # DOM utilities
    # ------------------------------------------------------------------

    def calculate_dom_distance(self, node1, node2):
        if node1 is node2:
            return 0

        ancestors1 = list(node1.parents)
        ancestors2 = list(node2.parents)

        if node2 in ancestors1:
            return ancestors1.index(node2)
        if node1 in ancestors2:
            return ancestors2.index(node1)

        common_ancestor = None
        for anc in ancestors1:
            if anc in ancestors2:
                common_ancestor = anc
                break

        if not common_ancestor:
            return 999

        return ancestors1.index(common_ancestor) + ancestors2.index(common_ancestor)

    SEMANTIC_CLASS_HINTS = (
        'title', 'headline', 'heading', 'content', 'article', 'entry', 'post',
        'body', 'description', 'summary', 'date', 'time', 'published', 'author',
    )
    NOISE_CLASS_HINTS = ('active', 'lazy', 'visible', 'js-', 'is-')

    def _pick_best_class(self, classes):
        """Prefer a class that looks semantically meaningful over an arbitrary
        first/utility class (fixes selectors keyed off unrelated utility classes)."""
        cleaned = []
        for c in classes:
            c_lower = c.lower()
            if any(w in c_lower for w in self.NOISE_CLASS_HINTS):
                continue
            cleaned.append(c)

        if not cleaned:
            return None

        for c in cleaned:
            c_lower = c.lower()
            if any(hint in c_lower for hint in self.SEMANTIC_CLASS_HINTS):
                return c

        # Fall back to the longest non-hashed-looking class name (short/hashed
        # utility classes like "a1b2" or "mt-2" are usually not discriminating).
        non_hashy = [c for c in cleaned if not re.fullmatch(r'[a-z0-9]{1,3}|[a-z]+-[0-9]+', c.lower())]
        pool = non_hashy or cleaned
        return max(pool, key=len)

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
                best_class = self._pick_best_class(classes)
                if best_class:
                    identifier += f".{best_class}"

            parent = current.parent
            if parent:
                siblings = parent.find_all(current.name, recursive=False)
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    identifier += f":nth-of-type({index})"

            path.append(identifier)
            current = parent

        path.reverse()
        return " > ".join(path)

    # ------------------------------------------------------------------
    # Shared voting/validation
    # ------------------------------------------------------------------

    def vote_on_selectors(self, selectors, total_urls, majority_fraction=0.5):
        """Single, consistent consensus policy used by every healer:
        - need at least 2 agreeing samples out of >1 URL tested, or
        - if only one URL was testable at all, accept a single result.
        Returns (best_selector, best_count) or (None, 0).
        """
        valid = [s for s in selectors if s]
        if not valid:
            return None, 0

        counts = Counter(valid)
        best_selector, best_count = counts.most_common(1)[0]

        if total_urls <= 1:
            return best_selector, best_count

        if best_count >= 2 and (best_count / len(valid)) > majority_fraction:
            return best_selector, best_count

        return None, 0

    def run_diagnostics(self):
        raise NotImplementedError("Subclasses must implement run_diagnostics")

#project/management/auto_healer/resolvers.py
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

    def _best_src(self, elem):
        """Pull a usable, single-URL src out of an element, handling srcset properly
        instead of returning the raw multi-candidate string."""
        for attr in ('data-lazy', 'data-src', 'src', 'media-url', 'data-video', 'poster'):
            val = elem.get(attr)
            if val:
                return val

        srcset = elem.get('srcset')
        if srcset:
            # srcset format: "url1 480w, url2 800w, ..." -> take the last (usually largest) candidate
            parts = [p.strip() for p in srcset.split(',') if p.strip()]
            if parts:
                first_token = parts[-1].split()[0]
                if first_token:
                    return first_token

        return elem.get('id')

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
            if id(elem) in seen:
                continue
            seen.add(id(elem))

            parent_has_bad_class = False
            for parent in elem.parents:
                if parent.name in ['head', 'noscript', 'aside', 'nav', 'footer']:
                    parent_has_bad_class = True
                    break
                if parent.get('class'):
                    p_classes = " ".join(parent.get('class')).lower()
                    if any(c in p_classes for c in ['sidebar', 'right-column', 'widgets', 'timeline', 'related', 'feed', 'stream', 'comments', 'recommend', 'slider', 'carousel', 'promo', 'podcast', 'audio', 'briefing', 'banner', 'advert', 'sponsor', 'adbox', 'insideind']):
                        parent_has_bad_class = True
                        break

            if parent_has_bad_class:
                continue

            src = self._best_src(elem)
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

                meta_str = f"{elem.get('id', '')} {' '.join(elem.get('class', []))}".lower()
                filename = src_lower.rsplit('/', 1)[-1]
                # Word-boundary check applied only to id/class/filename (not the full path),
                # so a real path segment like /wp-content/uploads/ can never trip 'ads'.
                if re.search(r'\b(icon|logo|avatar|pixel|spacer|ads|author|yazar)\b', meta_str) or \
                   re.search(r'\b(icon|logo|avatar|pixel|spacer|author|yazar)\b', filename):
                    continue

            valid_candidates.append(elem)
        return valid_candidates

    def find_image_by_h1_proximity(self, soup):
        h1_tag = self.get_h1_or_fallback(soup)
        if not h1_tag:
            return None

        candidates = self.get_all_media_candidates(soup)
        if not candidates:
            return None

        best_candidate = None
        min_distance = float('inf')

        for elem in candidates:
            try:
                distance = self.calculate_dom_distance(h1_tag, elem)
            except ValueError:
                continue
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

        if not article_text:
            return None

        candidates = self.get_all_media_candidates(soup)
        if not candidates:
            return None

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
        if not candidates:
            return None

        best_cand = None
        max_score = -1

        for cand in candidates:
            score = 10
            src = str(self._best_src(cand) or '')

            if any(audio_key in src.lower() for audio_key in ['spotify', 'soundcloud', 'audio', 'podcast']):
                continue
            if cand.name == 'iframe' and not any(k in src.lower() for k in ['youtube', 'vimeo', 't.me', 'embed', 'video', 'player']):
                score = 0
                continue
            if cand.name == 'video':
                score += 50
            elif cand.name in ['iframe', 'embed-content'] and any(k in src.lower() for k in ['youtube', 'vimeo', 'video', 'embed', 'player', 't.me']):
                score += 50

            if any(k in src.lower() for k in ['hero', 'large', 'cover', 'main', 'article', 'feature']):
                score += 30

            width = cand.get('width', '0')
            height = cand.get('height', '0')
            if str(width).isdigit() and str(height).isdigit():
                w, h = int(width), int(height)
                if w > 400:
                    score += 20
                if w > h:
                    score += 10

            if score > max_score:
                max_score = score
                best_cand = cand

        return best_cand

    def run_diagnostics(self):
        soups = [s for _, s in self.iter_cleaned_soups()]
        total_urls = len(soups)
        if total_urls == 0:
            return None

        # Tier 1: OpenGraph / Twitter / itemprop meta, checked across all
        # fetched samples (not just the first) before committing.
        meta_rule = self.resolve_from_value_tier(
            soups,
            lambda s: self.check_meta_tags(s, self.meta_tags),
            min_len=6,
        )
        if meta_rule:
            return {"resolution_type": "meta", "rule": meta_rule}

        generated_selectors = []

        for soup in soups:
            target_node_tfidf = self.find_image_by_tf_idf(soup)
            target_node_heur = self.find_image_by_heuristic_score(soup)
            target_node_h1 = self.find_image_by_h1_proximity(soup)

            votes = []
            if target_node_h1:
                votes.append(target_node_h1)
            if target_node_tfidf:
                votes.append(target_node_tfidf)
            if target_node_heur:
                votes.append(target_node_heur)

            winner_tag = None
            if votes:
                vote_counts = Counter(votes)
                most_common_tag, count = vote_counts.most_common(1)[0]
                if count >= 2:
                    winner_tag = most_common_tag

            if not winner_tag and target_node_heur:
                winner_tag = target_node_heur

            if winner_tag:
                new_selector = self.generate_css_selector(winner_tag)
                generated_selectors.append(new_selector)

        best_selector, best_count = self.vote_on_selectors(generated_selectors, total_urls)
        if best_selector:
            return {"resolution_type": "css_selector", "rule": best_selector}
        return None

#project/management/auto_healer/resolvers.py
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
        self.json_ld_keys = ["datePublished", "dateModified", "uploadDate"]

    def is_valid_date_format(self, text):
        if not text:
            return False
        numeric_pattern = re.compile(r'\b(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]20\d{2})\b')
        if numeric_pattern.search(text):
            return True
            
        textual_pattern = re.compile(r'\b\d{1,2}\s+[a-zA-Zа-яА-ЯəşçğıöüƏŞÇĞIÖÜ\u10D0-\u10FA]+(?:\s+20\d{2})?\b', re.IGNORECASE)
        if textual_pattern.search(text):
            return True
        return False

    def find_date_node(self, soup):
        # <time datetime="..."> is the single most reliable signal — machine-readable
        # and standardized — so it's checked first and preferred over any text match.
        for tag in soup.find_all('time'):
            if tag.has_attr('datetime'):
                return tag
        for tag in soup.find_all('time'):
            if self.is_valid_date_format(tag.get_text()):
                return tag

        itemprop_tags = soup.find_all(attrs={"itemprop": re.compile(r'datePublished|dateModified|uploadDate', re.I)})
        if itemprop_tags:
            return itemprop_tags[0]

        date_keywords = ['date', 'time', 'pubdate', 'timestamp', 'post-meta', 'article-date', 'yayin-tarihi', 'saat']
        candidates = []
        for tag in soup.find_all(['span', 'div', 'p', 'li']):
            class_str = " ".join(tag.get('class', [])).lower()
            id_str = tag.get('id', '').lower()
            if any(kw in class_str or kw in id_str for kw in date_keywords):
                if self.is_valid_date_format(tag.get_text()):
                    # Deprioritize anything that looks like it belongs to a related/teaser block
                    if tag.find_parent(class_=re.compile(r'related|recommend|teaser|widget', re.I)):
                        continue
                    candidates.append(tag)

        return candidates[0] if candidates else None

    def run_diagnostics(self):
        pairs = list(self.iter_cleaned_soups())
        soups = [s for _, s in pairs]
        total_urls = len(soups)
        if total_urls == 0:
            return None

        # Tier 1: JSON-LD structured date, checked across all fetched samples.
        json_ld_rule = self.resolve_from_value_tier(
            soups,
            lambda s: (self.get_json_ld_value(s, self.json_ld_keys), {"source": "json_ld", "keys": self.json_ld_keys}),
            min_len=4,
        )
        if json_ld_rule:
            return {"resolution_type": "meta", "rule": json_ld_rule}

        # Tier 2: standard meta tags, same cross-sample check.
        meta_rule = self.resolve_from_value_tier(
            soups,
            lambda s: self.check_meta_tags(s, self.meta_tags),
            min_len=4,
        )
        if meta_rule:
            return {"resolution_type": "meta", "rule": meta_rule}

        generated_selectors = []
        url_date_matches = []
        ###############
        for url, soup in pairs:
            if "formulanews.ge" in url:
                candidate = get_formulanews_date_candidate(soup)
                if candidate and validate_candidate(candidate):
                    # Helper qaytaran css selector və ya dəyəri birbaşa rule kimi götürürük
                    return {
                        "resolution_type": candidate.resolution_type, 
                        "rule": candidate.rule
                    }
            if "lent.az" in url:
                canditate= get_lentaz_date_candidate(soup)
                if soup.select_one('.news_img span'):
                    return {
                        "resolution_type": candidate.resolution_type, 
                        "rule": candidate.rule
                    }
                    
            date_node = self.find_date_node(soup)
            if date_node:
                selector = self.generate_css_selector(date_node)
                generated_selectors.append(selector)
            else:
                url_date_match = re.search(r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2})', url)
                if url_date_match:
                    url_date_matches.append(url_date_match.group(1))
       
        best_selector, best_count = self.vote_on_selectors(generated_selectors, total_urls)
        if best_selector:
            return {"resolution_type": "css_selector", "rule": best_selector}

        if url_date_matches and (len(url_date_matches) >= 2 or total_urls == 1):
            return {"resolution_type": "url_regex", "rule": r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2})'}

        return None


#project/management/auto_healer/resolvers.py
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
        self.json_ld_keys = ["headline", "name"]

    def find_title(self, soup):
        if is_mamul_domain(soup):
            from management.auto_healer.helpers.mamul_helper import get_mamul_title
            mamul_title = get_mamul_title(soup)
            if mamul_title:
                return mamul_title

        article_tag = soup.find('article')
        target_container = article_tag if article_tag else soup

        header_tag = target_container.find('header')
        if header_tag:
            h1_in_header = header_tag.find('h1')
            if h1_in_header:
                return h1_in_header

        h1_tag = target_container.find('h1') or soup.find('h1')
        if h1_tag:
            return h1_tag

        h2_tag = target_container.find('h2') or soup.find('h2')
        if h2_tag:
            return h2_tag

        heading_divs = soup.find_all(['div', 'span', 'header'], class_=lambda x: x and any(v in x.lower() for v in ['title', 'headline', 'heading']))
        if not heading_divs:
            return None

        for element in heading_divs:
            if element.find_parent(['head', 'noscript', 'aside', 'nav', 'footer']):
                continue
            if element.find_parent(class_=lambda x: x and any(c in x.lower() for c in ['sidebar', 'right-column', 'widgets'])):
                continue
            classes = ' '.join(element.get('class', [])).lower()
            if any(w in classes for w in ['uptitle', 'subtitle', 'descr', 'meta', 'date']):
                continue
            return element
        return None

    def run_diagnostics(self):
        pairs = list(self.iter_cleaned_soups())
        total_urls = len(pairs)
        if total_urls == 0:
            return None

        generated_selectors = []

        for url, soup in pairs:
            # JSON-LD headline is what search engines themselves trust, so it's
            # a strong ground-truth signal used here to cross-check the DOM
            # guess per-URL (see below) rather than as its own short-circuit
            # tier -- a title's exact on-page text can legitimately differ
            # slightly in punctuation/casing from the JSON-LD headline, so
            # committing to JSON-LD as the resolution *value* would sometimes
            # be less faithful to what the page actually renders than the
            # real DOM node is.
            json_ld_headline = self.get_json_ld_value(soup, self.json_ld_keys)

            target_node = self.find_title(soup)
            if target_node:
                node_text = target_node.get_text(strip=True)
                # Sanity check: if JSON-LD disagrees wildly with the DOM guess (e.g. the
                # DOM guess grabbed a section heading instead of the article title),
                # don't let it poison the vote for this URL.
                if json_ld_headline and node_text:
                    if json_ld_headline[:15].lower() not in node_text.lower() and node_text[:15].lower() not in json_ld_headline.lower():
                        continue
                new_selector = self.generate_css_selector(target_node)
                if new_selector:
                    generated_selectors.append(new_selector)

        best_selector, best_count = self.vote_on_selectors(generated_selectors, total_urls)
        if best_selector:
            return {"resolution_type": "css_selector", "rule": best_selector}
        return None

#project/management/auto_healer/resolvers.py
class DescriptionAutoHealer(BaseAutoHealer):
    def __init__(self, source_id, test_urls, shared_soups):
        super().__init__(source_id, test_urls, shared_soups)
        self.meta_tags = [
            {"tag": "meta", "attrs": {"property": "og:description"}},
            {"tag": "meta", "attrs": {"name": "description"}},
            {"tag": "meta", "attrs": {"property": "twitter:description"}},
            {"tag": "meta", "attrs": {"itemprop": "description"}}
        ]
        self.json_ld_keys = ["description"]

    def find_description(self, soup):
        desc_classes = ['lead', 'summary', 'excerpt', 'description', 'subtitle']
        desc_elements = soup.find_all(['div', 'p', 'span', 'h2', 'h3'], class_=lambda x: x and any(v in str(x).lower() for v in desc_classes))

        if desc_elements:
            for element in desc_elements:
                if element.find_parent(['nav', 'footer', 'aside', 'header']):
                    continue
                if element.text and len(element.text.strip()) > 15:
                    return element

        hgroups = soup.find_all('hgroup')
        for hgroup in hgroups:
            p_in_hgroup = hgroup.find(['p', 'h2', 'h3'])
            if p_in_hgroup and len(p_in_hgroup.text.strip()) > 15:
                return p_in_hgroup

        article_body = soup.find(['article', 'main']) or soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
        if article_body:
            paragraphs = article_body.find_all('p')
            for p in paragraphs:
                if p.text and len(p.text.strip()) > 30:
                    return p
        return None

    def run_diagnostics(self):
        pairs = list(self.iter_cleaned_soups())
        soups = [s for _, s in pairs]
        total_urls = len(soups)
        if total_urls == 0:
            return None

        # Tier 1: JSON-LD description, checked across all fetched samples.
        json_ld_rule = self.resolve_from_value_tier(
            soups,
            lambda s: (self.get_json_ld_value(s, self.json_ld_keys), {"source": "json_ld", "keys": self.json_ld_keys}),
            min_len=15,
        )
        if json_ld_rule:
            return {"resolution_type": "meta", "rule": json_ld_rule}

        # Tier 2: standard meta description, same cross-sample check.
        meta_rule = self.resolve_from_value_tier(
            soups,
            lambda s: self.check_meta_tags(s, self.meta_tags),
            min_len=6,
        )
        if meta_rule:
            return {"resolution_type": "meta", "rule": meta_rule}

        generated_selectors = []

        for url, soup in pairs:
            # Tier 3: DOM search.
            target_node = self.find_description(soup)
            if target_node:
                new_selector = self.generate_css_selector(target_node)
                if new_selector:
                    generated_selectors.append(new_selector)

        best_selector, best_count = self.vote_on_selectors(generated_selectors, total_urls)
        if best_selector:
            return {"resolution_type": "css_selector", "rule": best_selector}
        return None

#project/management/auto_healer/resolvers.py
class ContentAutoHealer(BaseAutoHealer):
    POSITIVE_HINTS = re.compile(r'article|content|entry|main|post|story|text', re.IGNORECASE)
    NEGATIVE_HINTS = re.compile(r'item|gallery|comment|footnote|foot|nav|sidebar|sponsor|share|social|widget|advert|banner|related|promo|masthead|byline|caption|teaser|header|timestamp|dateline|meta\b', re.IGNORECASE)
    MIN_PARAGRAPH_LEN = 25

    # ------------------------------------------------------------------
    # Fast path: semantic class-name search (kept for well-marked-up sites)
    # ------------------------------------------------------------------

    def _find_by_semantic_class(self, search_scope):
        from management.auto_healer.content_signals import (
            classes_for_noise_check, NOISE_WRAPPER_HINTS, has_duplicate_siblings,
        )
        content_pattern = re.compile(r'content-body|content-inner|article-body|post-content|entry-content|story-body|article-text|page-content|main-content|article_content|article__body|\bcontent\b', re.IGNORECASE)
        content_elements = search_scope.find_all(['div', 'article', 'section'], class_=content_pattern)

        scored = []
        for element in content_elements:
            if element.find_parent(['nav', 'footer', 'aside', 'header']):
                continue
            element_classes = classes_for_noise_check(element)
            parent_classes = " ".join(
                classes_for_noise_check(p) for p in element.parents if getattr(p, 'attrs', None) is not None
            )
            if NOISE_WRAPPER_HINTS.search(element_classes) or NOISE_WRAPPER_HINTS.search(parent_classes):
                continue
            if has_duplicate_siblings(element):
                continue

            paragraphs = element.find_all('p')  # note: recursive, on purpose -- nested wrappers are the common case
            text_len = len(element.get_text(strip=True))
            if len(paragraphs) >= 2 or text_len > 200:
                scored.append((text_len + len(paragraphs) * 50, element))

        if scored:
            # Text length only grows as you go up the tree, so scoring by
            # raw length alone always favors the outermost matching
            # ancestor (which then drags in header/title text too). Prefer
            # the most specific (innermost) candidate instead: drop any
            # match that itself contains another match.
            elements = [e for _, e in scored]
            specific = [(sc, e) for sc, e in scored if not any(o is not e and o in e.descendants for o in elements)]
            pool = specific or scored
            pool.sort(key=lambda x: x[0], reverse=True)
            return pool[0][1]

        semantic_elements = search_scope.find_all(['article', 'main'])
        scored = []
        for element in semantic_elements:
            paragraphs = element.find_all('p')
            text_len = len(element.get_text(strip=True))
            if len(paragraphs) >= 2 or text_len > 200:
                scored.append((text_len + len(paragraphs) * 50, element))
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1]

        return None

    # ------------------------------------------------------------------
    # Fallback: text-density scoring (Readability/Arc90-style)
    #
    # This needs no class-name vocabulary at all. It scores every paragraph-
    # like node on real textual signal, propagates that score up to its
    # container, and picks the container with the most/best real prose,
    # then rejects anything that looks like a link farm (nav/related blocks)
    # by link-density. This is what makes it work on sites with hashed
    # CSS-module class names, no semantic markup, or conventions we've
    # never seen before -- the previous "search from body" fallback only
    # ever looked at *direct* <p> children, which real CMSs almost never
    # use (paragraphs are wrapped one or two levels deep), so it silently
    # found nothing on the majority of real sites.
    # ------------------------------------------------------------------

    def _class_id_weight(self, node):
        weight = 0
        for attr in ('class', 'id'):
            val = node.get(attr)
            if not val:
                continue
            val_str = " ".join(val) if isinstance(val, list) else str(val)
            if self.NEGATIVE_HINTS.search(val_str):
                weight -= 25
            if self.POSITIVE_HINTS.search(val_str):
                weight += 25
        return weight

    def _score_dom_by_density(self, search_scope):
        scores = {}  # id(node) -> [score, node]

        text_bearing = list(search_scope.find_all(['p', 'pre', 'td', 'blockquote']))

        # Many sites use <div> instead of <p> for paragraphs -- catch those by
        # looking at each div's *own* direct text (not text inherited from
        # children), so a wrapper div doesn't get double-counted as its own paragraph.
        for div in search_scope.find_all('div'):
            direct_text = ''.join(t for t in div.find_all(string=True, recursive=False)).strip()
            if len(direct_text) >= self.MIN_PARAGRAPH_LEN:
                text_bearing.append(div)

        for node in text_bearing:
            if node.find_parent(['nav', 'footer', 'aside', 'header']):
                continue
            text = node.get_text(strip=True)
            if len(text) < self.MIN_PARAGRAPH_LEN:
                continue

            base_score = 1
            base_score += text.count(',')
            base_score += min(int(len(text) / 100), 3)

            parent = node.parent
            grandparent = parent.parent if parent is not None else None

            for target, decay in ((parent, 1.0), (grandparent, 0.5)):
                if target is None or target.name in ('body', '[document]'):
                    continue
                key = id(target)
                if key not in scores:
                    scores[key] = [self._class_id_weight(target), target]
                scores[key][0] += base_score * decay

        return scores

    def _link_density(self, node):
        from management.auto_healer.content_signals import link_density
        return link_density(node)

    def _validate_content_node(self, node, h1_tag=None):
        # Delegates to the single canonical implementation shared with
        # candidates.py -- see content_signals.py for why this used to be
        # two separately-maintained copies that drifted out of sync.
        from management.auto_healer.content_signals import validate_content_node
        return validate_content_node(node, h1_tag=h1_tag)

    def find_content_by_density(self, search_scope, h1_tag=None):
        scores = self._score_dom_by_density(search_scope)
        if not scores:
            return None

        ranked = sorted(scores.values(), key=lambda x: x[0], reverse=True)

        for score, node in ranked[:5]:
            if self._validate_content_node(node, h1_tag=h1_tag):
                return node

        return None

    def find_content(self, soup):
        data_target = soup.find(attrs={"data-article-body": "true"}) or soup.find(attrs={"data-body-type": "bodyblocks"})
        if data_target and not data_target.find_parent(['nav', 'footer', 'aside', 'header']):
            return data_target

        h1_tag = soup.find('h1')
        search_scope = soup
        if h1_tag:
            # Deliberately NOT including 'div' here: find_parent returns the
            # NEAREST match, and an h1 almost always sits inside some small
            # wrapper div (e.g. div.article__header) that holds only the
            # headline -- narrowing the scope to that div excludes the actual
            # body, which sits as a *sibling* of the header, not inside it.
            # Only climb into a named semantic container, which is far less
            # likely to be a title-only wrapper.
            parent_article = h1_tag.find_parent(['article', 'main', 'section'])
            if parent_article:
                # Extra safety net even for named containers: if it's barely
                # bigger than the headline itself, it's still a header-only
                # wrapper -- don't narrow into it.
                h1_len = len(h1_tag.get_text(strip=True))
                scope_len = len(parent_article.get_text(strip=True))
                if scope_len > h1_len * 3:
                    search_scope = parent_article

        node = self._find_by_semantic_class(search_scope)
        if self._validate_content_node(node, h1_tag=h1_tag):
            return node

        # No usable class/id vocabulary on this page (or it failed validation)
        # -- fall back to pure structural/statistical analysis.
        node = self.find_content_by_density(search_scope, h1_tag=h1_tag)
        if self._validate_content_node(node, h1_tag=h1_tag):
            return node

        return None

    def run_diagnostics(self):
        pairs = list(self.iter_cleaned_soups())
        total_urls = len(pairs)
        if total_urls == 0:
            return None

        generated_selectors = []

        for url, soup in pairs:
            target_node = self.find_content(soup)
            if target_node:
                new_selector = self.generate_css_selector(target_node)
                generated_selectors.append(new_selector)

        best_selector, best_count = self.vote_on_selectors(generated_selectors, total_urls)
        if best_selector:
            return {"resolution_type": "css_selector", "rule": best_selector}
        return None