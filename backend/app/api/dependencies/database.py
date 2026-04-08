"""
Database Dependencies
Provide database sessions to routes
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.database.session import async_session_maker
from app.core.cache import Cache

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis() -> Cache:
    """
    Get Redis cache client
    """
    cache = Cache()
    await cache.init()
    try:
        yield cache
    finally:
        await cache.close()