from __future__ import annotations

from pydantic import BaseModel, Field


class MediaInput(BaseModel):
    media_type: str = "IMAGE"
    file_url: str
    is_thumbnail: bool = False
    sequence: int = 0
    created_by_id: int | None = None


class VariantAttributeInput(BaseModel):
    attribute_slug: str
    value: str


class VariantInput(BaseModel):
    external_id: str | None = None
    sku: str
    name: str | None = None
    price: float
    old_price: float | None = None
    cost_price: float = 0.0
    stock_quantity: int = 0
    weight: float = 0.0
    width: float = 0.0
    height: float = 0.0
    length: float = 0.0
    is_active: bool = True
    created_by_id: int | None = None
    attribute_values: list[VariantAttributeInput] = Field(default_factory=list)
    media: list[MediaInput] = Field(default_factory=list)


class ProductInput(BaseModel):
    external_id: str | None = None
    name: str
    slug: str
    description: str | None = None
    short_description: str | None = None
    is_active: bool = True
    average_rating: float = 0.0
    reviews_count: int = 0
    category_slug: str
    category_name: str | None = None
    brand_slug: str | None = None
    brand_name: str | None = None
    created_by_id: int | None = None
    variants: list[VariantInput] = Field(default_factory=list)
    media: list[MediaInput] = Field(default_factory=list)


class ScrapeBatch(BaseModel):
    products: list[ProductInput] = Field(default_factory=list)
