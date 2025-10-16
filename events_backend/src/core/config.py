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
        ENV: Runtime environment name (e.g., development, production).
        UVICORN_HOST: Host interface for Uvicorn.
        UVICORN_PORT: Port for Uvicorn.
    """

    # Default to local SQLite file in the container/app working directory
    DATABASE_URL: str = Field(default="sqlite:///./app.db", description="SQLAlchemy database URL")
    # Comma-separated CORS origins for the frontend
    CORS_ORIGINS: str = Field(default="http://localhost:3000", description="Comma-separated CORS origins")
    # Extra envs commonly provided by process managers; including them prevents validation issues
    ENV: str = Field(default="development", description="Environment name: development | local | production")
    UVICORN_HOST: str = Field(default="0.0.0.0", description="Uvicorn host")
    UVICORN_PORT: int = Field(default=3001, description="Uvicorn port")

    # Ignore any additional environment variables so startup never fails on unknown keys
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # PUBLIC_INTERFACE
    def cors_origins_list(self) -> List[str]:
        """
        Return CORS origins as a list, splitting by comma and stripping whitespace.

        In development/local environments, ensure http://localhost:3000 is allowed by default
        to support the React dev server, even if the environment variable is unset or empty.
        """
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        env_lower = self.ENV.lower().strip()
        if env_lower in ("dev", "develop", "development", "local"):
            # Ensure localhost:3000 is present for local React dev server
            if "http://localhost:3000" not in origins:
                origins.append("http://localhost:3000")
        # Fallback: if still empty for any reason, default to localhost:3000 to avoid preflight failures
        if not origins:
            origins = ["http://localhost:3000"]
        return origins


@lru_cache()
# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


# Instantiate a module-level settings for convenience imports
settings = get_settings()
