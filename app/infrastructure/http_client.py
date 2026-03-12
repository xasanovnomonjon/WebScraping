from __future__ import annotations

import requests
from fake_useragent import UserAgent

from app.domain.interfaces import PageFetcher


class RequestsPageFetcher(PageFetcher):
    def __init__(self, timeout: int, retries: int) -> None:
        self._timeout = timeout
        self._retries = max(1, retries)
        self._user_agent = UserAgent()

    def fetch(self, url: str) -> str:
        last_error: Exception | None = None
        for _ in range(self._retries):
            try:
                headers = {
                    "User-Agent": self._user_agent.random,
                    "Accept-Language": "uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                response = requests.get(url, headers=headers, timeout=self._timeout)
                response.raise_for_status()
                return response.text
            except Exception as error:
                last_error = error
        if last_error is not None:
            raise last_error
        raise RuntimeError("Unknown fetch error")
