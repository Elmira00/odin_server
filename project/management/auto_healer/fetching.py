# project/management/auto_healer/fetching.py
"""
Fetching layer, extracted out of tasks.py. Has no Celery/Redis/Django-model
dependency on purpose.
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
        # services.py-dəki kimi sadə başlıq (anti-botların diqqətini çəkməmək üçün)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0", 
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

                if len(soup.get_text(strip=True)) < 20:
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