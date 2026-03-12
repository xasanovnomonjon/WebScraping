from __future__ import annotations

from pathlib import Path

import typer
from rich import print

from app.application.scrape_product_use_case import ScrapeProductUseCase
from app.application.scrape_texnomart_store_use_case import ScrapeTexnomartStoreUseCase
from app.application.scrape_texnomart_use_case import ScrapeTexnomartUseCase
from app.core.config import settings
from app.core.logger import setup_logging
from app.infrastructure.html_product_parser import GenericHtmlProductParser
from app.infrastructure.http_client import RequestsPageFetcher
from app.infrastructure.json_template_repository import JsonTemplateProductRepository
from app.infrastructure.texnomart_catalog_parser import TexnomartCatalogParser
from app.infrastructure.texnomart_product_parser import TexnomartProductParser

app = typer.Typer(help="Web scraping CLI for products.json template")

DEFAULT_STORE_CATEGORY_URLS = [
    "https://texnomart.uz/katalog/kabeli/",
    "https://texnomart.uz/katalog/aksessuary-dlya-telefonov/",
    "https://texnomart.uz/katalog/zaryadnye-ustroistva/",
    "https://texnomart.uz/katalog/naushniki/",
    "https://texnomart.uz/katalog/gadzhety/",
    "https://texnomart.uz/katalog/smartfony/",
    "https://texnomart.uz/katalog/noutbuki/",
    # Phone categories
    "https://texnomart.uz/katalog/knopochnye-telefon/",
    "https://texnomart.uz/katalog/telefon-aksessuarlari/",
]


@app.command()
def scrape(url: list[str] = typer.Option(..., "--url", help="Product page URL(s)")) -> None:
    setup_logging()

    fetcher = RequestsPageFetcher(
        timeout=settings.scraper_timeout,
        retries=settings.scraper_retries,
    )
    parser = GenericHtmlProductParser()
    repository = JsonTemplateProductRepository(settings.scraper_output_path)

    use_case = ScrapeProductUseCase(fetcher=fetcher, parser=parser, repository=repository)
    count = use_case.execute(url)

    print(f"[green]Done:[/green] {count} product(s) processed into {settings.scraper_output_path}")


@app.command("scrape-texnomart")
def scrape_texnomart(
    catalog_url: str = typer.Option(
        "https://texnomart.uz/katalog/aksessuary-dlya-telefonov/",
        "--catalog-url",
        help="Texnomart category URL",
    ),
    max_products: int = typer.Option(30, "--max-products", help="Max products to process"),
    catalog_html_file: str | None = typer.Option(
        None,
        "--catalog-html-file",
        help="Optional local category HTML file for product URL extraction",
    ),
) -> None:
    setup_logging()

    fetcher = RequestsPageFetcher(timeout=settings.scraper_timeout, retries=settings.scraper_retries)
    category_slug = catalog_url.rstrip("/").split("/")[-1] or "aksessuary-dlya-telefonov"
    catalog_parser = TexnomartCatalogParser()
    product_parser = TexnomartProductParser(default_category_slug=category_slug)
    repository = JsonTemplateProductRepository(settings.scraper_output_path)

    use_case = ScrapeTexnomartUseCase(
        fetcher=fetcher,
        catalog_parser=catalog_parser,
        product_parser=product_parser,
        repository=repository,
    )

    catalog_html = None
    if catalog_html_file:
        catalog_html = Path(catalog_html_file).read_text(encoding="utf-8")

    count = use_case.execute(catalog_url=catalog_url, max_products=max_products, catalog_html=catalog_html)
    print(f"[green]Done:[/green] {count} product(s) processed into {settings.scraper_output_path}")


@app.command("parse-local-product")
def parse_local_product(
    html_file: str = typer.Option("app/product_page.html", "--html-file", help="Local product HTML file"),
    source_url: str = typer.Option(
        "https://texnomart.uz/product/detail/354961/",
        "--source-url",
        help="Source URL used as canonical fallback",
    ),
) -> None:
    setup_logging()

    parser = TexnomartProductParser(default_category_slug="aksessuary-dlya-telefonov")
    repository = JsonTemplateProductRepository(settings.scraper_output_path)

    html = Path(html_file).read_text(encoding="utf-8")
    product = parser.parse_product(source_url, html)
    if product is None:
        print("[red]No product parsed from local html[/red]")
        raise typer.Exit(code=1)

    repository.add_or_update_products([product])
    print(f"[green]Done:[/green] local product parsed into {settings.scraper_output_path}")


@app.command("scrape-texnomart-store")
def scrape_texnomart_store(
    category_url: list[str] = typer.Option(
        [],
        "--category-url",
        help="Texnomart category URL(s). If empty, uses built-in store categories.",
    ),
    max_pages_per_category: int = typer.Option(
        10,
        "--max-pages-per-category",
        help="How many catalog pages to traverse per category",
    ),
    max_products_per_category: int = typer.Option(
        0,
        "--max-products-per-category",
        help="Limit products per category (0 = no limit)",
    ),
) -> None:
    setup_logging()

    categories = category_url or DEFAULT_STORE_CATEGORY_URLS

    fetcher = RequestsPageFetcher(timeout=settings.scraper_timeout, retries=settings.scraper_retries)
    catalog_parser = TexnomartCatalogParser()
    repository = JsonTemplateProductRepository(settings.scraper_output_path)

    def parser_factory(category_slug: str) -> TexnomartProductParser:
        return TexnomartProductParser(default_category_slug=category_slug)

    use_case = ScrapeTexnomartStoreUseCase(
        fetcher=fetcher,
        catalog_parser=catalog_parser,
        repository=repository,
        product_parser_factory=parser_factory,
    )

    count = use_case.execute(
        category_urls=categories,
        max_pages_per_category=max_pages_per_category,
        max_products_per_category=max_products_per_category,
    )
    print(f"[green]Done:[/green] {count} product(s) processed into {settings.scraper_output_path}")


if __name__ == "__main__":
    app()

