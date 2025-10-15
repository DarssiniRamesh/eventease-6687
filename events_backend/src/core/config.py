"""
Application configuration using Pydantic Settings.

Loads environment variables from .env if present.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: SQLAlchemy database URL. Defaults to local SQLite file.
        CORS_ORIGINS: Comma-separated list of allowed CORS origins for the frontend.
    """

    DATABASE_URL: str = Field(default="sqlite:///./events.db", description="SQLAlchemy database URL")
    CORS_ORIGINS: str = Field(default="http://localhost:3000", description="Comma-separated CORS origins")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # PUBLIC_INTERFACE
    def cors_origins_list(self) -> List[str]:
        """
        Return CORS origins as a list, splitting by comma and stripping whitespace.
        """
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


# Instantiate a module-level settings for convenience imports
settings = get_settings()
