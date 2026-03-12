from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    scraper_timeout: int = Field(default=20, alias="SCRAPER_TIMEOUT")
    scraper_retries: int = Field(default=3, alias="SCRAPER_RETRIES")
    scraper_output_path: Path = Field(default=Path("products.json"), alias="SCRAPER_OUTPUT_PATH")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
