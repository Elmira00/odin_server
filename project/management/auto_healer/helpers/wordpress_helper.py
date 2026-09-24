#project/management/auto_healer/helpers/wordpress_helper.py
"""
Fires on ANY WordPress-based source (a large fraction of regional news
sites run WordPress) -- not on one named domain. When it fires, it can
resolve title/description/date/image directly from WordPress's own JSON
REST API, which is far more reliable than parsing rendered HTML at all.
"""
import re
import requests
from urllib.parse import urljoin
from management.auto_healer.helpers.base_helper import BaseHelper
from management.auto_healer.helpers.registry import register_helper
from management.auto_healer.candidates import Candidate


@register_helper
class WordPressApiHelper(BaseHelper):
    name = "wordpress_api"
    tier = 0
    fields = ("title", "description", "content", "image", "shared_date")

    def applies(self, soup) -> bool:
        if soup.find("link", attrs={"rel": "https://api.w.org/"}):
            return True
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and "wordpress" in str(generator.get("content", "")).lower():
            return True
        return False

    def _fetch_post_json(self, soup, url):
        api_link = soup.find("link", attrs={"rel": "https://api.w.org/"})
        if not api_link or not api_link.get("href"):
            return None
        api_base = api_link["href"]
        # WordPress permalinks don't map 1:1 to post IDs, so resolve via slug search.
        slug_match = re.search(r'/([a-z0-9-]+)/?(?:\.html)?$', url.rstrip('/'))
        if not slug_match:
            return None
        slug = slug_match.group(1)
        try:
            resp = requests.get(
                urljoin(api_base, "posts"),
                params={"slug": slug},
                timeout=8,
            )
            data = resp.json()
            return data[0] if isinstance(data, list) and data else None
        except Exception:
            return None

    def get_candidates(self, soup, field, url):
        post = self._fetch_post_json(soup, url)
        if not post:
            return []

        key_map = {
            "title": lambda p: p.get("title", {}).get("rendered"),
            "description": lambda p: p.get("excerpt", {}).get("rendered"),
            "shared_date": lambda p: p.get("date_gmt") or p.get("date"),
            "image": lambda p: (p.get("_embedded", {}) or {})
                .get("wp:featuredmedia", [{}])[0].get("source_url"),
            "content": lambda p: p.get("content", {}).get("rendered"),
        }
        getter = key_map.get(field)
        if not getter:
            return []

        value = getter(post)
        if not value:
            return []

        if field in ("title", "description", "content"):
            value = re.sub(r'<[^>]+>', '', value).strip()

        return [Candidate(
            field=field,
            resolution_type="api_json",
            rule={"source": "wordpress_api", "field": field},
            source=self.name,
            value=value,
            prior_confidence=0.9,  # structured API data, high trust
        )]