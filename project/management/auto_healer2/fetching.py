#odin2/project/management/auto_healer/fetching.py
"""
Fetching layer, extracted out of tasks.py. Has no Celery/Redis/Django-model
dependency on purpose -- it's used identically by trigger_healer.py (manual
testing, no Celery) and by tasks.py (production, Celery-driven). When the
new discovery pipeline eventually gets wired into tasks.py, this file does
not change at all; only the caller does.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Set

import requests
from bs4 import BeautifulSoup


@dataclass
class PageContext:
    url: str
    status_code: Optional[int] = None
    raw_html: Optional[bytes] = None
    shared_soup: Optional[BeautifulSoup] = None
    fetch_error: Optional[str] = None

    @property
    def is_fetch_successful(self) -> bool:
        return self.status_code == 200 and self.shared_soup is not None


class FetchManager:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def fetch_unique_urls(self, urls: Set[str]) -> Dict[str, PageContext]:
        contexts = {}
        for url in urls:
            contexts[url] = self._fetch_single(url)
        return contexts

    def _fetch_single(self, url: str) -> PageContext:
        context = PageContext(url=url)
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            context.status_code = response.status_code

            if response.status_code == 200:
                context.raw_html = response.content
                soup = BeautifulSoup(context.raw_html, "html.parser")

                if len(soup.get_text(strip=True)) < 500:
                    context.fetch_error = "anti_bot_or_empty"
                else:
                    context.shared_soup = soup
            else:
                context.fetch_error = f"http_{response.status_code}"

        except requests.exceptions.Timeout:
            context.fetch_error = "timeout"
        except requests.exceptions.RequestException:
            context.fetch_error = "network_error"

        return context