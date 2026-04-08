"""
Usage Repository
Database operations for usage tracking and analytics
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc

from app.database.repositories.base_repo import BaseRepository
from app.models.usage import UsageEvent
from app.database.session import async_session_maker

class UsageRepository(BaseRepository):
    """
    Usage repository for analytics and tracking
    """
    
    def __init__(self):
        super().__init__(UsageEvent)
    
    async def track_event(self, event: Dict[str, Any]):
        """
        Track usage event
        """
        await self.create(event)
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user usage statistics
        """
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        async with async_session_maker() as session:
            # Total counts
            total_messages = await self._count_events(session, user_id, "message")
            total_searches = await self._count_events(session, user_id, "search")
            total_documents = await self._count_events(session, user_id, "document_upload")
            
            # Today's counts
            today_messages = await self._count_events(session, user_id, "message", since=today)
            today_searches = await self._count_events(session, user_id, "search", since=today)
            
            return {
                "total": {
                    "messages": total_messages,
                    "searches": total_searches,
                    "documents": total_documents
                },
                "today": {
                    "messages": today_messages,
                    "searches": today_searches
                }
            }
    
    async def _count_events(self, session, user_id: str, event_type: str, since: Optional[datetime] = None) -> int:
        """Helper to count events"""
        stmt = select(func.count(UsageEvent.id)).where(
            UsageEvent.user_id == user_id,
            UsageEvent.event == event_type
        )
        
        if since:
            stmt = stmt.where(UsageEvent.created_at >= since)
        
        result = await session.execute(stmt)
        return result.scalar_one()
    
    async def count_active_users(self, days: int = 1) -> int:
        """
        Count active users in last N days
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        async with async_session_maker() as session:
            stmt = select(func.count(func.distinct(UsageEvent.user_id))).where(
                UsageEvent.created_at >= since
            )
            result = await session.execute(stmt)
            return result.scalar_one()