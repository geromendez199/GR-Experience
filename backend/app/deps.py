"""Common dependency providers for FastAPI routes."""
from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator

import redis.asyncio as aioredis
from fastapi import Depends

from .config import Settings, get_settings
from .dataio.parquet_store import ParquetStore


@lru_cache(maxsize=1)
def _get_parquet_store() -> ParquetStore:
    settings = get_settings()
    return ParquetStore(root=settings.data_dir / "parquet", partition_cols=settings.parquet_partition_cols)


def get_parquet_store() -> ParquetStore:
    return _get_parquet_store()


async def get_redis(settings: Settings = Depends(get_settings)) -> AsyncIterator[aioredis.Redis]:
    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


def get_settings_dependency() -> Settings:
    return get_settings()
