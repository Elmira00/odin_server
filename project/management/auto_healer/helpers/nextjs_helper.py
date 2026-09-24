#project/management/auto_healer/helpers/nextjs_helper.py
"""
Fires on ANY site built with Next.js (__NEXT_DATA__) or Nuxt (window.__NUXT__)
-- again, a platform signature, not a domain. These frameworks embed the
exact data the page was rendered from as JSON in the page source, so pulling
values straight from that blob is more reliable than any DOM heuristic.
"""
import re
import json
from management.auto_healer.helpers.base_helper import BaseHelper
from management.auto_healer.helpers.registry import register_helper
from management.auto_healer.candidates import Candidate

FIELD_KEY_CANDIDATES = {
    "title": ["title", "headline", "name"],
    "description": ["description", "excerpt", "summary"],
    "shared_date": ["datePublished", "publishedAt", "published_at", "date"],
    "image": ["image", "imageUrl", "thumbnail", "coverImage"],
    "content": ["content", "body", "articleBody", "html"],
}


class NextJsHelper(BaseHelper):
    name = "nextjs_state_blob"
    tier = 0
    fields = ("title", "description", "content", "image", "shared_date")

    def applies(self, soup) -> bool:
        return soup.find("script", id="__NEXT_DATA__") is not None

    def _load_blob(self, soup):
        tag = soup.find("script", id="__NEXT_DATA__")
        if not tag or not tag.string:
            return None
        try:
            return json.loads(tag.string)
        except Exception:
            return None

    def _deep_find(self, obj, keys, max_depth=6, _depth=0):
        """Search a nested dict/list for the first value under any of the
        given keys. Generic on purpose -- every site's Next.js props shape
        differs, so we search structurally instead of hardcoding a path."""
        if _depth > max_depth:
            return None
        if isinstance(obj, dict):
            for k in keys:
                if k in obj and obj[k]:
                    return obj[k]
            for v in obj.values():
                result = self._deep_find(v, keys, max_depth, _depth + 1)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self._deep_find(item, keys, max_depth, _depth + 1)
                if result:
                    return result
        return None

    def get_candidates(self, soup, field, url):
        blob = self._load_blob(soup)
        if not blob:
            return []

        keys = FIELD_KEY_CANDIDATES.get(field)
        if not keys:
            return []

        value = self._deep_find(blob.get("props", blob), keys)
        if not value or not isinstance(value, str):
            return []

        if field == "content":
            value = re.sub(r'<[^>]+>', '', value).strip()

        return [Candidate(
            field=field,
            resolution_type="api_json",
            rule={"source": "nextjs_state_blob", "field": field, "keys": keys},
            source=self.name,
            value=value.strip(),
            prior_confidence=0.85,
        )]


register_helper(NextJsHelper)