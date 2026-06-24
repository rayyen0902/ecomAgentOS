"""Async SQLAlchemy session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings

_settings = get_settings()
engine = create_async_engine(_settings.database_url, echo=_settings.app_env == "development")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncGenerator, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_maker() as session:
        yield session
