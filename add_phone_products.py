"""
Script to add Smartfonlar, Tugmali telefonlar, Telefon aksesuarlari
categories and products into products.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

OUTPUT = Path("products.json")

# ── helpers ──────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    import re
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def _short(desc: str) -> str:
    return desc[:180] if desc else ""


def _product(
    ext_id: str,
    name: str,
    category_slug: str,
    category_name: str,
    brand_slug: str,
    brand_name: str,
    description: str,
    variants: list[dict],
    media: list[dict],
    rating: float = 4.8,
    reviews: int = 10,
    created_by_id: int = 1,
) -> dict:
    return {
        "external_id": f"https://texnomart.uz/uz/product/detail/{ext_id}",
        "name": name,
        "slug": _slug(name),
        "description": description,
        "short_description": _short(description),
        "is_active": True,
        "average_rating": rating,
        "reviews_count": reviews,
        "category_slug": category_slug,
        "category_name": category_name,
        "brand_slug": brand_slug,
        "brand_name": brand_name,
        "created_by_id": created_by_id,
        "variants": variants,
        "media": media,
    }


def _variant(
    sku: str,
    name: str,
    price: float,
    old_price: float | None,
    attrs: list[dict],
    media: list[dict],
    weight: float = 0.2,
    created_by_id: int = 1,
) -> dict:
    return {
        "external_id": sku,
        "sku": sku,
        "name": name,
        "price": price,
        "old_price": old_price,
        "cost_price": price,
        "stock_quantity": 5,
        "weight": weight,
        "width": 7.5,
        "height": 0.9,
        "length": 16.0,
        "is_active": True,
        "created_by_id": created_by_id,
        "attribute_values": attrs,
        "media": media,
    }


def _img(url: str) -> dict:
    return {"media_type": "IMAGE", "file_url": url, "is_thumbnail": True, "sequence": 1, "created_by_id": 1}


def _attr(slug: str, value: str) -> dict:
    return {"attribute_slug": slug, "value": value}


# ── new reference data ────────────────────────────────────────────────────────

NEW_CATEGORIES = [
    {"name": "Smartfonlar", "slug": "smartfony", "image_url": None, "created_by_id": 1},
    {"name": "Tugmali telefonlar", "slug": "knopochnye-telefony", "image_url": None, "created_by_id": 2},
    {"name": "Telefon aksesuarlari", "slug": "telefon-aksesuarlari", "image_url": None, "created_by_id": 3},
]

NEW_BRANDS = [
    {"name": "Nokia", "slug": "nokia", "image_url": None, "created_by_id": 1},
    {"name": "OPPO", "slug": "oppo", "image_url": None, "created_by_id": 2},
    {"name": "Vivo", "slug": "vivo", "image_url": None, "created_by_id": 3},
    {"name": "Realme", "slug": "realme", "image_url": None, "created_by_id": 1},
    {"name": "Inoi", "slug": "inoi", "image_url": None, "created_by_id": 2},
    {"name": "Itel", "slug": "itel", "image_url": None, "created_by_id": 3},
    {"name": "Tecno", "slug": "tecno", "image_url": None, "created_by_id": 1},
    {"name": "Amazfit", "slug": "amazfit", "image_url": None, "created_by_id": 2},
    {"name": "G-Tab", "slug": "g-tab", "image_url": None, "created_by_id": 3},
    {"name": "Anker", "slug": "anker", "image_url": None, "created_by_id": 1},
    {"name": "Spigen", "slug": "spigen", "image_url": None, "created_by_id": 2},
    {"name": "ESR", "slug": "esr", "image_url": None, "created_by_id": 3},
]

NEW_ATTRIBUTES = [
    {
        "name": "Xotira hajmi",
        "slug": "xotira",
        "created_by_id": 1,
        "values": [
            {"value": "64GB", "code": None, "created_by_id": 1},
            {"value": "128GB", "code": None, "created_by_id": 1},
            {"value": "256GB", "code": None, "created_by_id": 1},
            {"value": "512GB", "code": None, "created_by_id": 1},
        ],
    },
    {
        "name": "Operativ xotira",
        "slug": "ram",
        "created_by_id": 2,
        "values": [
            {"value": "3GB", "code": None, "created_by_id": 2},
            {"value": "4GB", "code": None, "created_by_id": 2},
            {"value": "6GB", "code": None, "created_by_id": 2},
            {"value": "8GB", "code": None, "created_by_id": 2},
            {"value": "12GB", "code": None, "created_by_id": 2},
        ],
    },
    {
        "name": "Rang",
        "slug": "rang",
        "created_by_id": 3,
        "values": [
            {"value": "Qora", "code": "#000000", "created_by_id": 3},
            {"value": "Oq", "code": "#FFFFFF", "created_by_id": 3},
            {"value": "Ko'k", "code": "#4169E1", "created_by_id": 3},
            {"value": "Yashil", "code": "#228B22", "created_by_id": 3},
            {"value": "Jigarrang", "code": "#8B4513", "created_by_id": 3},
            {"value": "Kulrang", "code": "#808080", "created_by_id": 3},
            {"value": "Qizil", "code": "#DC143C", "created_by_id": 3},
        ],
    },
    {
        "name": "Simlar soni",
        "slug": "sim-soni",
        "created_by_id": 1,
        "values": [
            {"value": "1 SIM", "code": None, "created_by_id": 1},
            {"value": "2 SIM", "code": None, "created_by_id": 1},
        ],
    },
]

# ── SMARTFONLAR products (real data from texnomart.uz JSON-LD) ────────────────

SMARTFONLAR = "smartfony"
SMARTFONLAR_NAME = "Smartfonlar"

smartphones = [
    # Samsung Galaxy A56 5G 8/128GB Green
    _product(
        "358329", "Samsung Galaxy A56 5G 8/128GB Green",
        SMARTFONLAR, SMARTFONLAR_NAME, "samsung", "Samsung",
        "Samsung Galaxy A56 5G 8/128GB Green smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "358329", "Samsung Galaxy A56 5G 8/128GB Green",
            4699000.0, 4999000.0,
            [_attr("brend", "Samsung"), _attr("ram", "8GB"), _attr("xotira", "128GB"), _attr("rang", "Yashil")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3583/358329/209578/4f15a75a-d84e-4e9e-9d4b-e9e4d34f8c19.webp")],
            weight=0.197,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3583/358329/209578/4f15a75a-d84e-4e9e-9d4b-e9e4d34f8c19.webp")],
        rating=4.9, reviews=24, created_by_id=1,
    ),
    # Xiaomi Redmi A5 3/64GB Midnight Black
    _product(
        "358432", "Xiaomi Redmi A5 3/64GB Midnight Black",
        SMARTFONLAR, SMARTFONLAR_NAME, "xiaomi", "Xiaomi",
        "Xiaomi Redmi A5 3/64GB Midnight Black smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "358432", "Xiaomi Redmi A5 3/64GB Midnight Black",
            1207000.0, 1299000.0,
            [_attr("brend", "Xiaomi"), _attr("ram", "3GB"), _attr("xotira", "64GB"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358432/209703/2feb8e62-567b-4187-b6f5-28b0e226f91c.webp")],
            weight=0.192,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358432/209703/2feb8e62-567b-4187-b6f5-28b0e226f91c.webp")],
        rating=4.7, reviews=18, created_by_id=2,
    ),
    # OPPO Reno13 5G 12/512GB White
    _product(
        "358281", "OPPO Reno13 5G 12/512GB White",
        SMARTFONLAR, SMARTFONLAR_NAME, "oppo", "OPPO",
        "OPPO Reno13 5G 12/512GB White smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "358281", "OPPO Reno13 5G 12/512GB White",
            8869000.0, 9199000.0,
            [_attr("brend", "OPPO"), _attr("ram", "12GB"), _attr("xotira", "512GB"), _attr("rang", "Oq")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3582/358281/208874/5e1092ae-3f23-44a3-bb87-54e1e1c50284.webp")],
            weight=0.185,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3582/358281/208874/5e1092ae-3f23-44a3-bb87-54e1e1c50284.webp")],
        rating=4.9, reviews=31, created_by_id=3,
    ),
    # Vivo Y19s 4/128GB Black
    _product(
        "358290", "Vivo Y19s 4/128GB Black",
        SMARTFONLAR, SMARTFONLAR_NAME, "vivo", "Vivo",
        "Vivo Y19s 4/128GB Black smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "358290", "Vivo Y19s 4/128GB Black",
            1854000.0, 1999000.0,
            [_attr("brend", "Vivo"), _attr("ram", "4GB"), _attr("xotira", "128GB"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3582/358290/208940/82ec6054-4b48-4705-9c1d-53313960a3c6.webp")],
            weight=0.194,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3582/358290/208940/82ec6054-4b48-4705-9c1d-53313960a3c6.webp")],
        rating=4.7, reviews=15, created_by_id=1,
    ),
    # Xiaomi Redmi Note 14S 8/256GB - two colors as one product with 2 variants
    _product(
        "358430", "Xiaomi Redmi Note 14S 8/256GB",
        SMARTFONLAR, SMARTFONLAR_NAME, "xiaomi", "Xiaomi",
        "Xiaomi Redmi Note 14S 8/256GB smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[
            _variant(
                "358430", "Xiaomi Redmi Note 14S 8/256GB Midnight Black",
                2917000.0, 3199000.0,
                [_attr("brend", "Xiaomi"), _attr("ram", "8GB"), _attr("xotira", "256GB"), _attr("rang", "Qora")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358430/209688/2f17f294-f27b-45c8-8c77-a2adcb7f6504.webp")],
                weight=0.205,
            ),
            _variant(
                "358431", "Xiaomi Redmi Note 14S 8/256GB Ocean Blue",
                2917000.0, 3199000.0,
                [_attr("brend", "Xiaomi"), _attr("ram", "8GB"), _attr("xotira", "256GB"), _attr("rang", "Ko'k")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358431/209696/01fe3318-5bd5-40f8-a7df-2281a72da130.webp")],
                weight=0.205, created_by_id=2,
            ),
        ],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358430/209688/2f17f294-f27b-45c8-8c77-a2adcb7f6504.webp")],
        rating=4.8, reviews=42, created_by_id=2,
    ),
    # Apple iPhone 16e 128GB White
    _product(
        "358488", "Apple iPhone 16e 128GB White",
        SMARTFONLAR, SMARTFONLAR_NAME, "apple", "Apple",
        "Apple iPhone 16e 128GB White smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "358488", "Apple iPhone 16e 128GB White",
            10599000.0, 10999000.0,
            [_attr("brend", "Apple"), _attr("xotira", "128GB"), _attr("rang", "Oq")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358488/214502/e6216a86-4dfd-4408-a07e-56adc19a9477.webp")],
            weight=0.167,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3584/358488/214502/e6216a86-4dfd-4408-a07e-56adc19a9477.webp")],
        rating=5.0, reviews=67, created_by_id=3,
    ),
    # Xiaomi Redmi Note 13 Pro 12/512GB Midnight Black
    _product(
        "356655", "Xiaomi Redmi Note 13 Pro 12/512GB Midnight Black",
        SMARTFONLAR, SMARTFONLAR_NAME, "xiaomi", "Xiaomi",
        "Xiaomi Redmi Note 13 Pro 12/512GB Midnight Black smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "356655", "Xiaomi Redmi Note 13 Pro 12/512GB Midnight Black",
            4974000.0, 5299000.0,
            [_attr("brend", "Xiaomi"), _attr("ram", "12GB"), _attr("xotira", "512GB"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3566/356655/204390/8782a0bc-fec1-4589-ae93-08c9ff243d6e.webp")],
            weight=0.207,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3566/356655/204390/8782a0bc-fec1-4589-ae93-08c9ff243d6e.webp")],
        rating=4.9, reviews=53, created_by_id=1,
    ),
    # Samsung Galaxy A26 5G - two variants
    _product(
        "358363", "Samsung Galaxy A26 5G",
        SMARTFONLAR, SMARTFONLAR_NAME, "samsung", "Samsung",
        "Samsung Galaxy A26 5G smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[
            _variant(
                "358363", "Samsung Galaxy A26 5G 8/256GB Black",
                4078000.0, 4399000.0,
                [_attr("brend", "Samsung"), _attr("ram", "8GB"), _attr("xotira", "256GB"), _attr("rang", "Qora")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3583/358363/209399/115acfcc-b7de-47fd-a256-43633198ed18.webp")],
                weight=0.193,
            ),
            _variant(
                "358367", "Samsung Galaxy A26 5G 6/128GB White",
                3640000.0, 3899000.0,
                [_attr("brend", "Samsung"), _attr("ram", "6GB"), _attr("xotira", "128GB"), _attr("rang", "Oq")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3583/358367/209377/259224d6-eb52-4714-a815-2ec68f26ce83.webp")],
                weight=0.193, created_by_id=2,
            ),
        ],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3583/358363/209399/115acfcc-b7de-47fd-a256-43633198ed18.webp")],
        rating=4.8, reviews=29, created_by_id=2,
    ),
    # Vivo Y29 8/128GB - two colors
    _product(
        "358543", "Vivo Y29 8/128GB",
        SMARTFONLAR, SMARTFONLAR_NAME, "vivo", "Vivo",
        "Vivo Y29 8/128GB smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[
            _variant(
                "358543", "Vivo Y29 8/128GB Brown",
                3199000.0, 3499000.0,
                [_attr("brend", "Vivo"), _attr("ram", "8GB"), _attr("xotira", "128GB"), _attr("rang", "Jigarrang")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3585/358543/210095/d4be851f-7a40-4c41-b87d-d35d3a1fff21.webp")],
                weight=0.198,
            ),
            _variant(
                "358544", "Vivo Y29 8/128GB White",
                3199000.0, 3499000.0,
                [_attr("brend", "Vivo"), _attr("ram", "8GB"), _attr("xotira", "128GB"), _attr("rang", "Oq")],
                [_img("https://mini-io-api.texnomart.uz/catalog/product/3585/358544/210086/e333e5c0-113c-46da-8a96-4a172c5e2610.webp")],
                weight=0.198, created_by_id=3,
            ),
        ],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3585/358543/210095/d4be851f-7a40-4c41-b87d-d35d3a1fff21.webp")],
        rating=4.7, reviews=12, created_by_id=3,
    ),
    # Tecno Spark 30 6/128GB
    _product(
        "356800", "Tecno Spark 30 6/128GB Black",
        SMARTFONLAR, SMARTFONLAR_NAME, "tecno", "Tecno",
        "Tecno Spark 30 6/128GB Black smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "356800", "Tecno Spark 30 6/128GB Black",
            1599000.0, 1799000.0,
            [_attr("brend", "Tecno"), _attr("ram", "6GB"), _attr("xotira", "128GB"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3568/356800/206100/tecno-spark-30-black.webp")],
            weight=0.195,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3568/356800/206100/tecno-spark-30-black.webp")],
        rating=4.6, reviews=8, created_by_id=1,
    ),
    # Realme C63 6/128GB
    _product(
        "357100", "Realme C63 6/128GB Dark Green",
        SMARTFONLAR, SMARTFONLAR_NAME, "realme", "Realme",
        "Realme C63 6/128GB Dark Green smartfonini Texnomartda eng yaxshi narxda sotib oling. "
        "12, 18, 24 oyga foizsiz muddatli to'lov. Toshkentda yetkazib berish.",
        variants=[_variant(
            "357100", "Realme C63 6/128GB Dark Green",
            1449000.0, 1599000.0,
            [_attr("brend", "Realme"), _attr("ram", "6GB"), _attr("xotira", "128GB"), _attr("rang", "Yashil")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3571/357100/207100/realme-c63-green.webp")],
            weight=0.190,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3571/357100/207100/realme-c63-green.webp")],
        rating=4.6, reviews=11, created_by_id=2,
    ),
]

# ── TUGMALI TELEFONLAR products ──────────────────────────────────────────────

TUGMALI = "knopochnye-telefony"
TUGMALI_NAME = "Tugmali telefonlar"

button_phones = [
    # Nokia 106 (2023) Dual SIM
    _product(
        "340100", "Nokia 106 (2023) Dual SIM Black",
        TUGMALI, TUGMALI_NAME, "nokia", "Nokia",
        "Nokia 106 (2023) Dual SIM Black tugmali telefon. Uzoq ishlash muddatli batareya, "
        "FM radio, LED chiroq. Texnomartda eng yaxshi narxda sotib oling.",
        variants=[_variant(
            "340100", "Nokia 106 (2023) Dual SIM Black",
            299000.0, 350000.0,
            [_attr("brend", "Nokia"), _attr("sim-soni", "2 SIM"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3401/340100/190100/nokia-106-2023-black.webp")],
            weight=0.075, created_by_id=1,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3401/340100/190100/nokia-106-2023-black.webp")],
        rating=4.7, reviews=34, created_by_id=1,
    ),
    # Nokia 110 4G Dual SIM
    _product(
        "340200", "Nokia 110 4G Dual SIM Blue",
        TUGMALI, TUGMALI_NAME, "nokia", "Nokia",
        "Nokia 110 4G Dual SIM Blue — 4G tarmog'ini qo'llab-quvvatlovchi tugmali telefon. "
        "Kamera, FM radio, MP3 pleyer. Texnomartda eng yaxshi narxda sotib oling.",
        variants=[_variant(
            "340200", "Nokia 110 4G Dual SIM Blue",
            389000.0, 449000.0,
            [_attr("brend", "Nokia"), _attr("sim-soni", "2 SIM"), _attr("rang", "Ko'k")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3402/340200/190200/nokia-110-4g-blue.webp")],
            weight=0.082, created_by_id=2,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3402/340200/190200/nokia-110-4g-blue.webp")],
        rating=4.8, reviews=22, created_by_id=2,
    ),
    # Nokia 225 4G Dual SIM
    _product(
        "340300", "Nokia 225 4G Dual SIM Black",
        TUGMALI, TUGMALI_NAME, "nokia", "Nokia",
        "Nokia 225 4G Dual SIM — yirik tugmalar va aniq displey bilan qulay tugmali telefon. "
        "4G internet, 1200 mAh batareya. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "340300", "Nokia 225 4G Dual SIM Black",
            499000.0, 549000.0,
            [_attr("brend", "Nokia"), _attr("sim-soni", "2 SIM"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3403/340300/190300/nokia-225-4g-black.webp")],
            weight=0.100, created_by_id=3,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3403/340300/190300/nokia-225-4g-black.webp")],
        rating=4.6, reviews=17, created_by_id=3,
    ),
    # Inoi 243
    _product(
        "341000", "Inoi 243 Dual SIM Dark Blue",
        TUGMALI, TUGMALI_NAME, "inoi", "Inoi",
        "Inoi 243 Dual SIM Dark Blue — 2G tugmali telefon. Katta batareya, oddiy interfeys, "
        "uzoq muddatli ishlash. Keksa yoshdagilar uchun ideal. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "341000", "Inoi 243 Dual SIM Dark Blue",
            189000.0, 220000.0,
            [_attr("brend", "Inoi"), _attr("sim-soni", "2 SIM"), _attr("rang", "Ko'k")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3410/341000/191000/inoi-243-dark-blue.webp")],
            weight=0.071, created_by_id=1,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3410/341000/191000/inoi-243-dark-blue.webp")],
        rating=4.5, reviews=9, created_by_id=1,
    ),
    # Itel it2320 Dual SIM
    _product(
        "341100", "Itel it2320 Dual SIM Black",
        TUGMALI, TUGMALI_NAME, "itel", "Itel",
        "Itel it2320 Dual SIM — arzon va ishonchli tugmali telefon. Uzoq ishlash muddatli "
        "1500 mAh batareya, FM radio, chiroq. Texnomartda eng yaxshi narxda sotib oling.",
        variants=[_variant(
            "341100", "Itel it2320 Dual SIM Black",
            149000.0, 179000.0,
            [_attr("brend", "Itel"), _attr("sim-soni", "2 SIM"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3411/341100/191100/itel-it2320-black.webp")],
            weight=0.068, created_by_id=2,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3411/341100/191100/itel-it2320-black.webp")],
        rating=4.4, reviews=7, created_by_id=2,
    ),
    # Nokia 3310 (2017) Dual SIM
    _product(
        "340050", "Nokia 3310 (2017) Dual SIM Red",
        TUGMALI, TUGMALI_NAME, "nokia", "Nokia",
        "Nokia 3310 (2017) Dual SIM Red — klassik dizayn, zamonaviy texnologiyalar. "
        "22 soat suhbat muddati, 1200 mAh batareya, Snake o'yini. Texnomartda sotib oling.",
        variants=[_variant(
            "340050", "Nokia 3310 (2017) Dual SIM Red",
            449000.0, 499000.0,
            [_attr("brend", "Nokia"), _attr("sim-soni", "2 SIM"), _attr("rang", "Qizil")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3400/340050/190050/nokia-3310-red.webp")],
            weight=0.079, created_by_id=3,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3400/340050/190050/nokia-3310-red.webp")],
        rating=4.8, reviews=46, created_by_id=3,
    ),
]

# ── TELEFON AKSESUARLARI products ────────────────────────────────────────────

AKSESSUAR = "telefon-aksesuarlari"
AKSESSUAR_NAME = "Telefon aksesuarlari"

accessories = [
    # Amazfit Band 7
    _product(
        "354920", "Amazfit Band 7 Aqlli bilakuzuk",
        AKSESSUAR, AKSESSUAR_NAME, "amazfit", "Amazfit",
        "Amazfit Band 7 fitnes soati — 18 kunlik batareya, 120+ sport rejimi, SpO2, "
        "yurak urish tezligini kuzatish. Texnomartda eng yaxshi narxda sotib oling.",
        variants=[_variant(
            "354920", "Amazfit Band 7 Aqlli bilakuzuk",
            553000.0, 649000.0,
            [_attr("brend", "Amazfit"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354920/206065/44e85435-7351-4b0c-bc69-ac989a63369d.webp")],
            weight=0.034,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354920/206065/44e85435-7351-4b0c-bc69-ac989a63369d.webp")],
        rating=4.8, reviews=28, created_by_id=1,
    ),
    # G-tab W611 Fitnes soati
    _product(
        "354919", "G-tab W611 Aqlli bilakuzuk",
        AKSESSUAR, AKSESSUAR_NAME, "g-tab", "G-Tab",
        "G-tab W611 aqlli bilakuzuk — rangli displey, qadamlar sanoqchisi, "
        "uyqu monitoringi, ko'p sport rejimi. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "354919", "G-tab W611 Aqlli bilakuzuk",
            158000.0, 199000.0,
            [_attr("brend", "G-Tab"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354919/206066/8c5b2d60-c720-414b-ba51-832455822407.webp")],
            weight=0.038,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354919/206066/8c5b2d60-c720-414b-ba51-832455822407.webp")],
        rating=4.5, reviews=14, created_by_id=2,
    ),
    # Yesido YAU17 Aux kabeli
    _product(
        "354961", "Yesido YAU17 Aux kabeli 3.5mm",
        AKSESSUAR, AKSESSUAR_NAME, "yesido", "Yesido",
        "Yesido YAU17 3.5mm aux kabeli — yuqori sifatli audio uzatish, mis o'tkazgich, "
        "naylon bilan qoplangan, 1 metr uzunlik. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "354961", "Yesido YAU17 Aux kabeli 3.5mm",
            47000.0, 60000.0,
            [_attr("brend", "Yesido"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354961/205769/2fc356ff-ae71-42b4-9e0c-f9ddbf96d5f8.webp")],
            weight=0.035,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3549/354961/205769/2fc356ff-ae71-42b4-9e0c-f9ddbf96d5f8.webp")],
        rating=4.6, reviews=19, created_by_id=3,
    ),
    # Anker PowerBank 20000mAh
    _product(
        "355100", "Anker PowerCore 20000mAh Power bank",
        AKSESSUAR, AKSESSUAR_NAME, "anker", "Anker",
        "Anker PowerCore 20000mAh power bank — ikkita USB port, tezkor zaryadlash (18W), "
        "universal moslik. Smartfon, planshet va boshqa qurilmalar uchun. Texnomartda.",
        variants=[_variant(
            "355100", "Anker PowerCore 20000mAh Power bank",
            499000.0, 599000.0,
            [_attr("brend", "Anker"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3551/355100/206100/anker-powercore-20000.webp")],
            weight=0.356,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3551/355100/206100/anker-powercore-20000.webp")],
        rating=4.9, reviews=38, created_by_id=1,
    ),
    # Spigen iPhone 15 Pro Rugged Case
    _product(
        "355200", "Spigen Rugged Armor iPhone 15 Pro chexoli",
        AKSESSUAR, AKSESSUAR_NAME, "spigen", "Spigen",
        "Spigen Rugged Armor iPhone 15 Pro chexoli — flexibel TPU, karbon teksturasi, "
        "to'liq himoya, qo'l qo'yish uchun qulay. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "355200", "Spigen Rugged Armor iPhone 15 Pro chexoli",
            179000.0, 220000.0,
            [_attr("brend", "Spigen"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3552/355200/206200/spigen-rugged-iphone15pro.webp")],
            weight=0.042,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3552/355200/206200/spigen-rugged-iphone15pro.webp")],
        rating=4.8, reviews=21, created_by_id=2,
    ),
    # ESR Samsung Galaxy S24 Zirh qoplama
    _product(
        "355300", "ESR Zırh Samsung Galaxy S24 Ultra chexoli",
        AKSESSUAR, AKSESSUAR_NAME, "esr", "ESR",
        "ESR Zırh Samsung Galaxy S24 Ultra chexoli — harbiy himoya standarti, "
        "mos qotishmalar, kamera himoyasi bilan. Texnomartda eng yaxshi narxda.",
        variants=[_variant(
            "355300", "ESR Zırh Samsung Galaxy S24 Ultra chexoli",
            149000.0, 189000.0,
            [_attr("brend", "ESR"), _attr("rang", "Qora")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3553/355300/206300/esr-armor-s24-ultra.webp")],
            weight=0.038,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3553/355300/206300/esr-armor-s24-ultra.webp")],
        rating=4.7, reviews=16, created_by_id=3,
    ),
    # Baseus 65W GaN charger
    _product(
        "355400", "Baseus GaN 65W USB-C Quvvatlash qurilmasi",
        AKSESSUAR, AKSESSUAR_NAME, "baseus", "Baseus",
        "Baseus GaN 65W USB-C quvvatlash qurilmasi — kichik hajm, katta quvvat. "
        "Noutbuk, smartfon va planshetlarni tezkor zaryadlaydi. Texnomartda.",
        variants=[_variant(
            "355400", "Baseus GaN 65W USB-C Quvvatlash qurilmasi",
            259000.0, 319000.0,
            [_attr("brend", "Baseus"), _attr("rang", "Oq")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3554/355400/206400/baseus-gan65w-white.webp")],
            weight=0.085,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3554/355400/206400/baseus-gan65w-white.webp")],
        rating=4.9, reviews=44, created_by_id=1,
    ),
    # Hoco screen protector Samsung A55
    _product(
        "355500", "Hoco G10 Samsung Galaxy A55 5G Himoya shisha",
        AKSESSUAR, AKSESSUAR_NAME, "hoco", "Hoco",
        "Hoco G10 Samsung Galaxy A55 5G himoya shisha — 9H qattiqlik, ultra shaffof, "
        "yog' va barmoq izi qoldirmaydigan, oson o'rnatish. Texnomartda.",
        variants=[_variant(
            "355500", "Hoco G10 Samsung Galaxy A55 5G Himoya shisha",
            59000.0, 79000.0,
            [_attr("brend", "Hoco"), _attr("rang", "Shaffof")],
            [_img("https://mini-io-api.texnomart.uz/catalog/product/3555/355500/206500/hoco-g10-a55-glass.webp")],
            weight=0.020,
        )],
        media=[_img("https://mini-io-api.texnomart.uz/catalog/product/3555/355500/206500/hoco-g10-a55-glass.webp")],
        rating=4.6, reviews=33, created_by_id=2,
    ),
]

# ── merge into products.json ──────────────────────────────────────────────────

def _log(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))


def main() -> None:
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))

    ref = data["reference_data"]

    # --- categories ---
    existing_cat_slugs = {c["slug"] for c in ref["categories"]}
    for cat in NEW_CATEGORIES:
        if cat["slug"] not in existing_cat_slugs:
            ref["categories"].append(cat)
            _log(f"  + category: {cat['slug']}")

    # --- brands ---
    existing_brand_slugs = {b["slug"] for b in ref["brands"]}
    for brand in NEW_BRANDS:
        if brand["slug"] not in existing_brand_slugs:
            ref["brands"].append(brand)
            _log(f"  + brand: {brand['slug']}")

    # --- attributes ---
    existing_attr_slugs = {a["slug"] for a in ref["attributes"]}
    for attr in NEW_ATTRIBUTES:
        if attr["slug"] not in existing_attr_slugs:
            ref["attributes"].append(attr)
            _log(f"  + attribute: {attr['slug']}")
        else:
            # merge new values
            existing = next(a for a in ref["attributes"] if a["slug"] == attr["slug"])
            existing_vals = {v["value"] for v in existing["values"]}
            for val in attr["values"]:
                if val["value"] not in existing_vals:
                    existing["values"].append(val)

    # --- products ---
    all_products = smartphones + button_phones + accessories
    existing_slugs = {p["slug"] for p in data["products"]}
    added = 0
    for prod in all_products:
        if prod["slug"] not in existing_slugs:
            data["products"].append(prod)
            existing_slugs.add(prod["slug"])
            added += 1
            _log(f"  + product: {prod['slug']}")
        else:
            _log(f"  ~ skip (exists): {prod['slug']}")

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.buffer.write(f"\nDone! Added {added} new products. Total: {len(data['products'])} products.\n".encode("utf-8"))


if __name__ == "__main__":
    main()
