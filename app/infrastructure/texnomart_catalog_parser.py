from __future__ import annotations

import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.domain.interfaces import CatalogParser


class TexnomartCatalogParser(CatalogParser):
    def parse_product_urls(self, source_url: str, html: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")

        urls: list[str] = []

        for script in soup.select("script[type='application/ld+json']"):
            content = (script.string or script.get_text() or "").strip()
            if not content:
                continue
            for obj in self._load_json_ld(content):
                if not isinstance(obj, dict):
                    continue
                if obj.get("@type") != "ItemList":
                    continue
                for item in obj.get("itemListElement", []) or []:
                    product = item.get("item", {}) if isinstance(item, dict) else {}
                    product_url = product.get("url") if isinstance(product, dict) else None
                    if isinstance(product_url, str) and "/product/detail/" in product_url:
                        urls.append(self._normalize_url(product_url, source_url))

        if not urls:
            for anchor in soup.select("a[href*='/product/detail/']"):
                href = anchor.get("href")
                if href:
                    urls.append(self._normalize_url(href, source_url))

        unique_urls: list[str] = []
        seen = set()
        for link in urls:
            if link in seen:
                continue
            seen.add(link)
            unique_urls.append(link)
        return unique_urls

    def _load_json_ld(self, text: str) -> list[dict]:
        try:
            payload = json.loads(text)
        except Exception:
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            return [payload]
        return []

    def _normalize_url(self, url: str, base: str) -> str:
        absolute = urljoin(base, url)
        absolute = absolute.replace("/uz/product/detail/", "/product/detail/")
        if absolute.endswith("/"):
            return absolute
        return f"{absolute}/"
