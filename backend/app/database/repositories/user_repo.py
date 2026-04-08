"""
User Repository
Database operations for users
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base_repo import BaseRepository
from app.database.session import async_session_maker
from app.models.user import User


class UserRepository(BaseRepository):
    """
    User repository with user-specific queries
    """
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        users = await self.get_many(email=email)
        return users[0] if users else None
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username – required for uniqueness check"""
        users = await self.get_many(username=username)
        return users[0] if users else None
    
    async def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        await self.update(user_id, {
            "last_login": datetime.utcnow()
        })
    
    async def count_new_users(self, date: datetime) -> int:
        """Count new users on a specific date"""
        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)
        async with async_session_maker() as session:
            stmt = select(func.count()).where(
                User.created_at >= start,
                User.created_at < end
            )
            result = await session.execute(stmt)
            return result.scalar_one()
    
    async def count_new_users_since(self, since: datetime) -> int:
        """Count new users since a given date"""
        async with async_session_maker() as session:
            stmt = select(func.count()).where(User.created_at >= since)
            result = await session.execute(stmt)
            return result.scalar_one()
    
    async def get_users_by_signup_date(self, date: datetime) -> List[str]:
        """Get user IDs who signed up on a specific date"""
        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)
        async with async_session_maker() as session:
            stmt = select(User.id).where(
                User.created_at >= start,
                User.created_at < end
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def update_stripe_customer(self, user_id: str, customer_id: str):
        """Update Stripe customer ID for user"""
        await self.update(user_id, {"stripe_customer_id": customer_id})