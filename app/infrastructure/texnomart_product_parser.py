from __future__ import annotations

import json
import re
from html import unescape
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.domain.entities import MediaInput, ProductInput, VariantAttributeInput, VariantInput
from app.domain.interfaces import ProductDetailParser


def _slugify(value: str) -> str:
    value = unescape(value).strip().lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value


def _to_float(raw: object) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    if raw is None:
        return 0.0
    normalized = str(raw).replace(",", ".")
    digits = re.sub(r"[^0-9.]", "", normalized)
    if not digits:
        return 0.0
    try:
        return float(digits)
    except ValueError:
        return 0.0


class TexnomartProductParser(ProductDetailParser):
    def __init__(self, default_category_slug: str = "aksessuary-dlya-telefonov") -> None:
        self._default_category_slug = default_category_slug

    def parse_product(self, source_url: str, html: str) -> ProductInput | None:
        soup = BeautifulSoup(html, "lxml")
        product_ld = self._find_product_ld(soup)

        canonical = self._meta_content(soup, "og:url") or source_url
        name = self._clean(product_ld.get("name") if product_ld else None) or self._title_fallback(soup)
        if not name:
            return None

        description = self._clean(product_ld.get("description") if product_ld else None) or self._meta_content(
            soup, "description"
        )
        brand_name = self._clean(product_ld.get("brand") if product_ld else None)
        if not brand_name:
            brand_name = self._extract_brand_from_characteristics(soup)

        images = self._extract_images(product_ld)
        if not images:
            main_image = self._meta_content(soup, "og:image")
            if main_image:
                images = [main_image]

        rating_value, reviews_count = self._extract_rating(product_ld)
        price, old_price = self._extract_prices(product_ld, soup)

        product_id = self._extract_product_id(canonical)
        sku = product_id or f"TXM-{_slugify(name)[:24].upper()}"

        category_name = self._extract_category_name(soup)
        category_slug = self._default_category_slug

        attributes = self._extract_attribute_values(soup)
        weight, width, height, length = self._extract_dimensions(attributes)
        if weight == 0.0 and width == 0.0 and height == 0.0 and length == 0.0:
            weight, width, height, length = self._extract_dimensions_from_raw_html(html)

        variant_media = [
            MediaInput(media_type="IMAGE", file_url=image, is_thumbnail=(idx == 0), sequence=idx + 1)
            for idx, image in enumerate(images)
        ]

        variant = VariantInput(
            external_id=product_id,
            sku=sku,
            name=name,
            price=price,
            old_price=old_price if old_price > 0 else None,
            cost_price=price,
            stock_quantity=0,
            weight=weight,
            width=width,
            height=height,
            length=length,
            attribute_values=attributes,
            media=variant_media,
        )

        brand_slug = _slugify(brand_name) if brand_name else self._guess_brand_slug_from_host(canonical)

        return ProductInput(
            external_id=canonical,
            name=name,
            slug=_slugify(name),
            description=description,
            short_description=(description[:180] if description else None),
            average_rating=rating_value,
            reviews_count=reviews_count,
            category_slug=category_slug,
            category_name=category_name,
            brand_slug=brand_slug,
            brand_name=brand_name,
            variants=[variant],
            media=variant_media,
        )

    def _find_product_ld(self, soup: BeautifulSoup) -> dict:
        for script in soup.select("script[type='application/ld+json']"):
            content = (script.string or script.get_text() or "").strip()
            if not content:
                continue
            for obj in self._load_json_ld(content):
                if isinstance(obj, dict) and obj.get("@type") == "Product":
                    return obj
        return {}

    def _load_json_ld(self, text: str) -> list[dict]:
        normalized = unescape(text).replace("\ufeff", "").strip()
        try:
            payload = json.loads(normalized)
        except Exception:
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            return [payload]
        return []

    def _extract_images(self, product_ld: dict) -> list[str]:
        image = product_ld.get("image") if isinstance(product_ld, dict) else None
        if isinstance(image, str) and image.strip():
            return [image.strip()]
        if isinstance(image, list):
            return [str(item).strip() for item in image if str(item).strip()]
        return []

    def _extract_rating(self, product_ld: dict) -> tuple[float, int]:
        rating = product_ld.get("aggregateRating", {}) if isinstance(product_ld, dict) else {}
        rating_value = _to_float(rating.get("ratingValue") if isinstance(rating, dict) else None)
        review_count = int(_to_float(rating.get("reviewCount") if isinstance(rating, dict) else None))
        return rating_value, review_count

    def _extract_prices(self, product_ld: dict, soup: BeautifulSoup) -> tuple[float, float]:
        offers = product_ld.get("offers", {}) if isinstance(product_ld, dict) else {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price = _to_float(offers.get("price") if isinstance(offers, dict) else None)

        if price <= 0:
            visible_price = soup.select_one(".product__price .font-bold")
            price = _to_float(visible_price.get_text(" ", strip=True) if visible_price else None)

        old_price_node = soup.select_one(".product__price .old-price")
        old_price = _to_float(old_price_node.get_text(" ", strip=True) if old_price_node else None)
        return price, old_price

    def _extract_attribute_values(self, soup: BeautifulSoup) -> list[VariantAttributeInput]:
        attributes: list[VariantAttributeInput] = []
        seen = set()
        for item in soup.select(".characteristic__item"):
            name_node = item.select_one(".characteristic__name")
            value_node = item.select_one(".characteristic__value")
            if not name_node or not value_node:
                continue
            attr_name = self._clean(name_node.get_text(" ", strip=True))
            attr_value = self._clean(value_node.get_text(" ", strip=True))
            if not attr_name or not attr_value:
                continue
            slug = _slugify(attr_name)
            key = (slug, attr_value.lower())
            if key in seen:
                continue
            seen.add(key)
            attributes.append(VariantAttributeInput(attribute_slug=slug, value=attr_value))
        return attributes

    def _extract_brand_from_characteristics(self, soup: BeautifulSoup) -> str | None:
        for item in soup.select(".characteristic__item"):
            name_node = item.select_one(".characteristic__name")
            value_node = item.select_one(".characteristic__value")
            if not name_node or not value_node:
                continue
            label = self._clean(name_node.get_text(" ", strip=True))
            if label and _slugify(label) == "brend":
                return self._clean(value_node.get_text(" ", strip=True))
        return None

    def _extract_dimensions(self, attributes: list[VariantAttributeInput]) -> tuple[float, float, float, float]:
        weight = 0.0
        width = 0.0
        height = 0.0
        length = 0.0

        for attr in attributes:
            slug = attr.attribute_slug
            value_num = self._extract_first_number(attr.value)
            if value_num <= 0:
                continue

            if slug in {"qadoq-ogirligi", "v-upakovke-ves", "weight", "ves"}:
                weight = value_num
            elif slug in {"qadoq-kengligi", "shirina", "width"}:
                width = value_num
            elif slug in {"qadoq-balandligi", "visota", "height"}:
                height = value_num
            elif slug in {"qadoq-uzunligi", "dlina", "length"}:
                length = value_num

        return weight, width, height, length

    def _extract_first_number(self, value: str) -> float:
        match = re.search(r"\d+(?:[\.,]\d+)?", value)
        if not match:
            return 0.0
        return _to_float(match.group(0))

    def _extract_dimensions_from_raw_html(self, html: str) -> tuple[float, float, float, float]:
        mappings = {
            "weight": ["Qadoq og'irligi", "Вес упаковки", "Qadoq vazni"],
            "length": ["Qadoq uzunligi", "Длина упаковки"],
            "width": ["Qadoq kengligi", "Ширина упаковки"],
            "height": ["Qadoq balandligi", "Высота упаковки"],
        }

        values: dict[str, float] = {
            "weight": 0.0,
            "width": 0.0,
            "height": 0.0,
            "length": 0.0,
        }

        for key, labels in mappings.items():
            values[key] = self._extract_dimension_by_labels(html, labels)

        return values["weight"], values["width"], values["height"], values["length"]

    def _extract_dimension_by_labels(self, html: str, labels: list[str]) -> float:
        for label in labels:
            pattern = re.compile(
                rf"name\s*:\s*\"{re.escape(label)}\"\s*,\s*value\s*:\s*\"([^\"]+)\"",
                re.IGNORECASE,
            )
            match = pattern.search(html)
            if match:
                return self._extract_first_number(match.group(1))
        return 0.0

    def _extract_category_name(self, soup: BeautifulSoup) -> str | None:
        for script in soup.select("script[type='application/ld+json']"):
            content = (script.string or script.get_text() or "").strip()
            if not content:
                continue
            for obj in self._load_json_ld(content):
                if not isinstance(obj, dict) or obj.get("@type") != "BreadcrumbList":
                    continue
                elements = obj.get("itemListElement") or []
                if not isinstance(elements, list):
                    continue
                if not elements:
                    continue
                last = elements[-1]
                if isinstance(last, dict):
                    return self._clean(last.get("name"))
        return None

    def _extract_product_id(self, url: str) -> str | None:
        match = re.search(r"/product/detail/(\d+)", url)
        if match:
            return match.group(1)
        return None

    def _meta_content(self, soup: BeautifulSoup, prop_or_name: str) -> str | None:
        node = soup.select_one(f"meta[property='{prop_or_name}']") or soup.select_one(
            f"meta[name='{prop_or_name}']"
        )
        if node and node.get("content"):
            return self._clean(node.get("content"))
        return None

    def _title_fallback(self, soup: BeautifulSoup) -> str | None:
        h1 = soup.select_one("h1")
        if h1:
            text = self._clean(h1.get_text(" ", strip=True))
            if text:
                return text
        title = soup.select_one("title")
        if title:
            text = self._clean(title.get_text(" ", strip=True))
            if text:
                return text.split(":")[0].strip()
        return None

    def _guess_brand_slug_from_host(self, url: str) -> str | None:
        host = urlparse(url).netloc
        if not host:
            return None
        root = host.split(".")[0]
        return _slugify(root)

    def _clean(self, value: object) -> str | None:
        if value is None:
            return None
        text = unescape(str(value)).replace("\xa0", " ").strip()
        text = re.sub(r"\s+", " ", text)
        return text or None
