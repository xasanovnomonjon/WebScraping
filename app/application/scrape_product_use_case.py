from __future__ import annotations

import logging

from app.domain.interfaces import PageFetcher, ProductParser, ProductRepository


class ScrapeProductUseCase:
    def __init__(
        self,
        fetcher: PageFetcher,
        parser: ProductParser,
        repository: ProductRepository,
    ) -> None:
        self._fetcher = fetcher
        self._parser = parser
        self._repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)

    def execute(self, urls: list[str]) -> int:
        all_products = []
        for url in urls:
            self._logger.info("Fetching: %s", url)
            html = self._fetcher.fetch(url)
            products = self._parser.parse(url, html)
            self._logger.info("Parsed %d products from %s", len(products), url)
            all_products.extend(products)

        if not all_products:
            self._logger.info("No products parsed")
            return 0

        self._repository.add_or_update_products(all_products)
        return len(all_products)
