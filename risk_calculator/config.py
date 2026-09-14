import sys
from functools import lru_cache
from pathlib import Path

from loguru import logger
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
    log_level: str = "INFO"
    log_json: bool = False

    # --- Database ---
    db_path: Path = Field(
        default=Path("portfolio.db"),
        description="Path to the SQLite database file",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging(settings: Settings) -> None:
    logger.remove()

    if settings.log_json:
        logger.add(sys.stdout, level=settings.log_level, serialize=True)
    else:
        logger.add(
            sink=sys.stdout,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        )
