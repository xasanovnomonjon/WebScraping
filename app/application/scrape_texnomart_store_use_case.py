from __future__ import annotations

import logging
from typing import Callable

from app.domain.interfaces import CatalogParser, PageFetcher, ProductDetailParser, ProductRepository


class ScrapeTexnomartStoreUseCase:
    def __init__(
        self,
        fetcher: PageFetcher,
        catalog_parser: CatalogParser,
        repository: ProductRepository,
        product_parser_factory: Callable[[str], ProductDetailParser],
    ) -> None:
        self._fetcher = fetcher
        self._catalog_parser = catalog_parser
        self._repository = repository
        self._product_parser_factory = product_parser_factory
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(
        self,
        category_urls: list[str],
        max_pages_per_category: int = 10,
        max_products_per_category: int = 0,
    ) -> int:
        total_parsed = 0

        for category_url in category_urls:
            category_slug = self._category_slug(category_url)
            product_urls = self._collect_product_urls(
                category_url=category_url,
                max_pages=max_pages_per_category,
            )

            if max_products_per_category > 0:
                product_urls = product_urls[:max_products_per_category]

            parser = self._product_parser_factory(category_slug)
            parsed_products = []

            for product_url in product_urls:
                try:
                    product_html = self._fetcher.fetch(product_url)
                    product = parser.parse_product(product_url, product_html)
                    if product:
                        parsed_products.append(product)
                except Exception as error:
                    self._logger.warning("Failed parsing %s: %s", product_url, error)

            if parsed_products:
                self._repository.add_or_update_products(parsed_products)
                total_parsed += len(parsed_products)
                self._logger.info(
                    "Category %s parsed %d products",
                    category_slug,
                    len(parsed_products),
                )

        return total_parsed

    def _collect_product_urls(self, category_url: str, max_pages: int) -> list[str]:
        seen_urls = set()
        ordered_urls: list[str] = []
        unchanged_pages = 0

        for page in range(1, max_pages + 1):
            page_url = self._page_url(category_url, page)
            try:
                html = self._fetcher.fetch(page_url)
            except Exception as error:
                self._logger.warning("Cannot fetch page %s: %s", page_url, error)
                break

            page_urls = self._catalog_parser.parse_product_urls(page_url, html)
            added = 0
            for url in page_urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                ordered_urls.append(url)
                added += 1

            if added == 0:
                unchanged_pages += 1
            else:
                unchanged_pages = 0

            if unchanged_pages >= 2:
                break

        return ordered_urls

    def _page_url(self, category_url: str, page: int) -> str:
        base = category_url.rstrip("/") + "/"
        if page <= 1:
            return base
        return f"{base}?page={page}"

    def _category_slug(self, category_url: str) -> str:
        return category_url.rstrip("/").split("/")[-1] or "unknown"
