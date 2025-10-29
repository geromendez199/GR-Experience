"""Application configuration settings for the GR-Experience backend."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Environment-driven application configuration."""

    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    cors_origins: str = Field("http://localhost:3000", env="CORS_ORIGINS")
    data_dir: Path = Field(Path("./data"), env="DATA_DIR")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    next_public_api_base_url: str = Field(
        "http://localhost:8000", env="NEXT_PUBLIC_API_BASE_URL"
    )
    model_dir: Path = Field(Path("./models"), env="MODEL_DIR")
    parquet_partition_cols: List[str] = Field(
        default_factory=lambda: ["session_id", "track"]
    )
    redis_cache_ttl_seconds: int = Field(300, env="REDIS_CACHE_TTL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @validator("data_dir", "model_dir", pre=True)
    def _expand_path(cls, value: Path | str) -> Path:
        return Path(value).expanduser().resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    return settings
