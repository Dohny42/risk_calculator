from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Risk Calculator API"

    # --- Database ---
    db_path: Path = Field(
        default=Path("portfolio.db"),
        description="Path to the SQLite database file",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
