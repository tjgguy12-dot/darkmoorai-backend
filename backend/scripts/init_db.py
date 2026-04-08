#!/usr/bin/env python3
"""
Initialize Database
Create tables and seed initial data
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.session import init_db, engine
from app.models.database import Base
from app.utils.logger import logger

async def main():
    """
    Initialize database
    """
    logger.info("Initializing database...")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
        # Close connection
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())