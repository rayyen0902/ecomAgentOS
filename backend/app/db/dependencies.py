"""Database dependencies for FastAPI."""

from collections.abc import AsyncGenerator

from app.db.session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncGenerator, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_maker() as session:
        yield session
