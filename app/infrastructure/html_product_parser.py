from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.domain.entities import MediaInput, ProductInput, VariantInput
from app.domain.interfaces import ProductParser


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value


def _extract_price(raw: str | None) -> float:
    if not raw:
        return 0.0
    digits = re.sub(r"[^0-9.]", "", raw)
    if not digits:
        return 0.0
    try:
        return float(digits)
    except ValueError:
        return 0.0


class GenericHtmlProductParser(ProductParser):
    def __init__(self, default_category_slug: str = "smartfonlar") -> None:
        self._default_category_slug = default_category_slug

    def parse(self, source_url: str, html: str) -> list[ProductInput]:
        soup = BeautifulSoup(html, "lxml")

        title = self._first_text(soup, ["h1", "meta[property='og:title']"])
        if not title:
            return []

        description = self._first_text(
            soup,
            ["meta[name='description']", ".product-description", "#description"],
        )
        image = self._first_attr(
            soup,
            ["meta[property='og:image']", ".product-image img", "img"],
            "content",
            fallback_attr="src",
        )
        price_text = self._first_text(soup, [".price", ".product-price", "[itemprop='price']"])
        price = _extract_price(price_text)

        host = urlparse(source_url).netloc
        brand_slug = host.split(".")[0] if host else None

        slug = _slugify(title)
        sku = f"{slug[:20].upper()}-001"

        variant = VariantInput(
            sku=sku,
            name=title,
            price=price,
            old_price=None,
            cost_price=price,
            stock_quantity=0,
            attribute_values=[],
            media=[
                MediaInput(
                    media_type="IMAGE",
                    file_url=image,
                    is_thumbnail=True,
                    sequence=1,
                )
            ]
            if image
            else [],
        )

        product = ProductInput(
            external_id=source_url,
            name=title,
            slug=slug,
            description=description,
            short_description=description[:180] if description else None,
            category_slug=self._default_category_slug,
            brand_slug=brand_slug,
            variants=[variant],
            media=[
                MediaInput(
                    media_type="IMAGE",
                    file_url=image,
                    is_thumbnail=True,
                    sequence=1,
                )
            ]
            if image
            else [],
        )
        return [product]

    def _first_text(self, soup: BeautifulSoup, selectors: list[str]) -> str | None:
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            if node.name == "meta":
                content = node.get("content")
                if content:
                    return content.strip()
            text = node.get_text(" ", strip=True)
            if text:
                return text
        return None

    def _first_attr(
        self,
        soup: BeautifulSoup,
        selectors: list[str],
        attr: str,
        fallback_attr: str | None = None,
    ) -> str | None:
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            value = node.get(attr)
            if not value and fallback_attr:
                value = node.get(fallback_attr)
            if value:
                return value.strip()
        return None
