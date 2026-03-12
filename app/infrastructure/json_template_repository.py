from __future__ import annotations

import json
from pathlib import Path

from app.domain.entities import ProductInput
from app.domain.interfaces import ProductRepository


class JsonTemplateProductRepository(ProductRepository):
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def add_or_update_products(self, products: list[ProductInput]) -> None:
        payload = self._read()
        existing_products = payload.setdefault("products", [])
        payload.setdefault("meta", {})
        payload.setdefault("reference_data", {})
        payload["reference_data"].setdefault("categories", [])
        payload["reference_data"].setdefault("brands", [])
        payload["reference_data"].setdefault("attributes", [])

        index_by_slug = {
            item.get("slug"): idx
            for idx, item in enumerate(existing_products)
            if item.get("slug")
        }

        product_dicts = [product.model_dump(mode="json") for product in products]
        self._merge_reference_data(payload, product_dicts)

        for product_data in product_dicts:
            slug = product_data.get("slug")
            if slug in index_by_slug:
                existing_products[index_by_slug[slug]] = product_data
            else:
                existing_products.append(product_data)

        self._write(payload)

    def _read(self) -> dict:
        if not self._file_path.exists():
            return {"meta": {}, "reference_data": {}, "products": []}
        with self._file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, payload: dict) -> None:
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _merge_reference_data(self, payload: dict, products: list[dict]) -> None:
        reference_data = payload["reference_data"]
        categories = reference_data["categories"]
        brands = reference_data["brands"]
        attributes = reference_data["attributes"]

        category_index = {item.get("slug"): item for item in categories if item.get("slug")}
        brand_index = {item.get("slug"): item for item in brands if item.get("slug")}
        attribute_index = {item.get("slug"): item for item in attributes if item.get("slug")}

        for product in products:
            category_slug = product.get("category_slug")
            if category_slug and category_slug not in category_index:
                category_item = {
                    "name": product.get("category_name") or category_slug.replace("-", " ").title(),
                    "slug": category_slug,
                    "image_url": None,
                    "created_by_id": product.get("created_by_id"),
                }
                categories.append(category_item)
                category_index[category_slug] = category_item

            brand_slug = product.get("brand_slug")
            if brand_slug and brand_slug not in brand_index:
                brand_item = {
                    "name": product.get("brand_name") or brand_slug.replace("-", " ").title(),
                    "slug": brand_slug,
                    "image_url": None,
                    "created_by_id": product.get("created_by_id"),
                }
                brands.append(brand_item)
                brand_index[brand_slug] = brand_item

            for variant in product.get("variants", []):
                for attr in variant.get("attribute_values", []):
                    attr_slug = attr.get("attribute_slug")
                    attr_value = attr.get("value")
                    if not attr_slug or not attr_value:
                        continue

                    attr_item = attribute_index.get(attr_slug)
                    if attr_item is None:
                        attr_item = {
                            "name": attr_slug.replace("-", " ").title(),
                            "slug": attr_slug,
                            "created_by_id": product.get("created_by_id"),
                            "values": [],
                        }
                        attributes.append(attr_item)
                        attribute_index[attr_slug] = attr_item

                    values = attr_item.setdefault("values", [])
                    exists = any(v.get("value") == attr_value for v in values)
                    if not exists:
                        values.append(
                            {
                                "value": attr_value,
                                "code": None,
                                "created_by_id": product.get("created_by_id"),
                            }
                        )
