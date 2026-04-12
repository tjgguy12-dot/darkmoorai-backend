"""
Database Session Management
SQLAlchemy async session configuration
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from typing import AsyncGenerator
import os

from app.config import config
from app.models.database import Base
from app.utils.logger import logger

# Use environment variable for database URL (Render provides this in production)
DATABASE_URL = os.getenv("DATABASE_URL", config.DATABASE_URL)

# Convert SQLite sync URL to async URL if needed
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    logger.info("Using async SQLite driver")
elif DATABASE_URL.startswith("postgresql://"):
    # Replace with asyncpg driver for PostgreSQL
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Using asyncpg driver for PostgreSQL")

# Create engine with production settings
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=config.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialize database connection and create tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """Close database connection"""
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def check_db_connection() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"healthy": True}
    except Exception as e:
        return {"healthy": False, "error": str(e)}