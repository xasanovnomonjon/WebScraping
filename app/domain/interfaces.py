from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import ProductInput


class PageFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str) -> str:
        raise NotImplementedError


class ProductParser(ABC):
    @abstractmethod
    def parse(self, source_url: str, html: str) -> list[ProductInput]:
        raise NotImplementedError


class ProductRepository(ABC):
    @abstractmethod
    def add_or_update_products(self, products: list[ProductInput]) -> None:
        raise NotImplementedError


class CatalogParser(ABC):
    @abstractmethod
    def parse_product_urls(self, source_url: str, html: str) -> list[str]:
        raise NotImplementedError


class ProductDetailParser(ABC):
    @abstractmethod
    def parse_product(self, source_url: str, html: str) -> ProductInput | None:
        raise NotImplementedError
