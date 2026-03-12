from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_IDS = [1, 2, 3]


def next_id(ids: list[int], state: dict[str, int]) -> int:
    value = ids[state["index"] % len(ids)]
    state["index"] += 1
    return value


def set_created_by_id(target: dict[str, Any], value: int) -> int:
    if target.get("created_by_id") != value:
        target["created_by_id"] = value
        return 1
    return 0


def process_products_json(payload: dict[str, Any], ids: list[int]) -> int:
    updated = 0
    state = {"index": 0}

    for product in payload.get("products", []) or []:
        if not isinstance(product, dict):
            continue

        product_admin_id = product.get("created_by_id")
        if product_admin_id is None:
            product_admin_id = next_id(ids, state)
        else:
            try:
                product_admin_id = int(product_admin_id)
            except (TypeError, ValueError):
                product_admin_id = next_id(ids, state)

        updated += set_created_by_id(product, product_admin_id)

        for variant in product.get("variants", []) or []:
            if not isinstance(variant, dict):
                continue

            updated += set_created_by_id(variant, product_admin_id)

            for media in variant.get("media", []) or []:
                if isinstance(media, dict):
                    updated += set_created_by_id(media, product_admin_id)

        for media in product.get("media", []) or []:
            if isinstance(media, dict):
                updated += set_created_by_id(media, product_admin_id)

    return updated


def parse_ids(raw_ids: str) -> list[int]:
    values = []
    for part in raw_ids.split(","):
        part = part.strip()
        if not part:
            continue
        values.append(int(part))
    if not values:
        raise ValueError("At least one id is required")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Set one admin ID per product and enforce the same created_by_id for that product, "
            "its variants, and all related media."
        )
    )
    parser.add_argument(
        "--file",
        default="products.json",
        help="Path to products.json (default: products.json)",
    )
    parser.add_argument(
        "--ids",
        default="1,2,3",
        help="Comma-separated IDs to rotate (default: 1,2,3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many rows would be updated without writing file",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ids = parse_ids(args.ids)

    payload = json.loads(path.read_text(encoding="utf-8"))
    updated_count = process_products_json(payload, ids)

    if args.dry_run:
        print(f"Dry run: {updated_count} created_by_id fields will be synchronized")
        return

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Synchronized {updated_count} created_by_id fields in {path}")


if __name__ == "__main__":
    main()
