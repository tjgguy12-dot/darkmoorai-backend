#!/usr/bin/env python3
"""
Seed Database
Add initial data for development
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.session import async_session_maker
from app.models.user import User
from app.models.subscription import Subscription
from app.utils.logger import logger

async def main():
    """
    Seed database with initial data
    """
    logger.info("Seeding database...")
    
    async with async_session_maker() as session:
        # Create admin user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = User(
            email="admin@darkmoor.ai",
            username="admin",
            hashed_password=pwd_context.hash("Admin123!"),
            full_name="Darkmoor Admin",
            role="admin",
            is_active=True,
            is_verified=True
        )
        
        session.add(admin_user)
        
        # Create sample free subscription
        free_sub = Subscription(
            user_id=admin_user.id,
            tier="free",
            status="active"
        )
        
        session.add(free_sub)
        
        await session.commit()
        
        logger.info(f"Created admin user: {admin_user.id}")
    
    logger.info("Database seeded successfully")

if __name__ == "__main__":
    asyncio.run(main())