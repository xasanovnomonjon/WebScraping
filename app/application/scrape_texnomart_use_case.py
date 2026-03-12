from __future__ import annotations

import logging

from app.domain.interfaces import CatalogParser, PageFetcher, ProductDetailParser, ProductRepository


class ScrapeTexnomartUseCase:
    def __init__(
        self,
        fetcher: PageFetcher,
        catalog_parser: CatalogParser,
        product_parser: ProductDetailParser,
        repository: ProductRepository,
    ) -> None:
        self._fetcher = fetcher
        self._catalog_parser = catalog_parser
        self._product_parser = product_parser
        self._repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(
        self,
        catalog_url: str,
        max_products: int | None = None,
        catalog_html: str | None = None,
    ) -> int:
        html = catalog_html if catalog_html is not None else self._fetcher.fetch(catalog_url)
        product_urls = self._catalog_parser.parse_product_urls(catalog_url, html)

        if max_products is not None and max_products > 0:
            product_urls = product_urls[:max_products]

        products = []
        for url in product_urls:
            try:
                page_html = self._fetcher.fetch(url)
                product = self._product_parser.parse_product(url, page_html)
                if product is not None:
                    products.append(product)
                    self._logger.info("Parsed product: %s", product.slug)
            except Exception as error:
                self._logger.warning("Failed parsing %s: %s", url, error)

        if products:
            self._repository.add_or_update_products(products)

        return len(products)
