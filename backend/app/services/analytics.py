"""
Analytics Service
Track and analyze user behavior and system performance
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.database.repositories.user_repo import UserRepository
from app.database.repositories.usage_repo import UsageRepository
from app.core.cache import Cache
from app.utils.logger import logger

class AnalyticsService:
    """
    Analytics and reporting service
    """
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.usage_repo = UsageRepository()
        self.cache = Cache()
    
    async def track_event(
        self,
        user_id: str,
        event_name: str,
        properties: Optional[Dict] = None
    ):
        """
        Track user event
        """
        event = {
            "user_id": user_id,
            "event": event_name,
            "properties": properties or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in Redis for real-time
        await self.cache.lpush("analytics:events", json.dumps(event), ttl=86400)
        
        # Also store in database (batched)
        await self.usage_repo.track_event(event)
        
        logger.debug(f"Event tracked: {event_name} for user {user_id}")
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics
        """
        # Get from cache or calculate
        cache_key = f"stats:user:{user_id}"
        cached = await self.cache.get(cache_key)
        
        if cached:
            return cached
        
        # Calculate stats
        stats = await self.usage_repo.get_user_stats(user_id)
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, stats, ttl=300)
        
        return stats
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide statistics
        """
        cache_key = "stats:system"
        cached = await self.cache.get(cache_key)
        
        if cached:
            return cached
        
        # Calculate
        total_users = await self.user_repo.count()
        active_today = await self.usage_repo.count_active_users(days=1)
        active_week = await self.usage_repo.count_active_users(days=7)
        active_month = await self.usage_repo.count_active_users(days=30)
        
        stats = {
            "total_users": total_users,
            "active_today": active_today,
            "active_week": active_week,
            "active_month": active_month,
            "messages_today": await self.usage_repo.count_messages(days=1),
            "messages_week": await self.usage_repo.count_messages(days=7),
            "documents_today": await self.usage_repo.count_documents(days=1),
            "documents_week": await self.usage_repo.count_documents(days=7),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.cache.set(cache_key, stats, ttl=300)
        
        return stats
    
    async def get_daily_active_users(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily active users for chart
        """
        result = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            count = await self.usage_repo.count_active_users_on_date(date)
            
            result.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return sorted(result, key=lambda x: x["date"])
    
    async def get_usage_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage trends over time
        """
        return {
            "users": await self.get_daily_active_users(days),
            "messages": await self.usage_repo.get_daily_messages(days),
            "documents": await self.usage_repo.get_daily_documents(days),
            "costs": await self.usage_repo.get_daily_costs(days)
        }
    
    async def get_top_users(self, metric: str = "messages", limit: int = 10) -> List[Dict]:
        """
        Get top users by metric
        """
        return await self.usage_repo.get_top_users(metric, limit)
    
    async def get_popular_searches(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        Get popular search queries
        """
        return await self.usage_repo.get_popular_searches(days, limit)
    
    async def get_popular_documents(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        Get most accessed documents
        """
        return await self.usage_repo.get_popular_documents(days, limit)
    
    async def get_source_usage(self, days: int = 7) -> Dict[str, int]:
        """
        Get usage breakdown by knowledge source
        """
        return await self.usage_repo.get_source_usage(days)
    
    async def get_error_rates(self, days: int = 7) -> Dict[str, Any]:
        """
        Get error rates over time
        """
        return await self.usage_repo.get_error_rates(days)
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate daily analytics report
        """
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        report = {
            "date": yesterday.strftime("%Y-%m-%d"),
            "summary": {
                "new_users": await self.user_repo.count_new_users(yesterday),
                "active_users": await self.usage_repo.count_active_users_on_date(yesterday),
                "messages": await self.usage_repo.count_messages_on_date(yesterday),
                "documents": await self.usage_repo.count_documents_on_date(yesterday),
                "searches": await self.usage_repo.count_searches_on_date(yesterday),
                "total_cost": await self.usage_repo.get_cost_on_date(yesterday)
            },
            "top_searches": await self.get_popular_searches(days=1, limit=5),
            "source_usage": await self.get_source_usage(days=1),
            "error_rate": await self.usage_repo.get_error_rate_on_date(yesterday)
        }
        
        return report
    
    async def generate_weekly_report(self) -> Dict[str, Any]:
        """
        Generate weekly analytics report
        """
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        report = {
            "week_start": week_ago.strftime("%Y-%m-%d"),
            "week_end": datetime.utcnow().strftime("%Y-%m-%d"),
            "summary": {
                "new_users": await self.user_repo.count_new_users_since(week_ago),
                "active_users": await self.usage_repo.count_active_users(days=7),
                "total_messages": await self.usage_repo.count_messages(days=7),
                "total_documents": await self.usage_repo.count_documents(days=7),
                "total_searches": await self.usage_repo.count_searches(days=7),
                "total_cost": await self.usage_repo.get_cost(days=7)
            },
            "daily_breakdown": await self.get_daily_active_users(7),
            "top_users": await self.get_top_users("messages", 10),
            "source_breakdown": await self.get_source_usage(7),
            "trends": await self.get_usage_trends(7)
        }
        
        return report
    
    async def generate_monthly_report(self) -> Dict[str, Any]:
        """
        Generate monthly analytics report
        """
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        report = {
            "month_start": month_ago.strftime("%Y-%m-%d"),
            "month_end": datetime.utcnow().strftime("%Y-%m-%d"),
            "summary": {
                "new_users": await self.user_repo.count_new_users_since(month_ago),
                "active_users": await self.usage_repo.count_active_users(days=30),
                "total_messages": await self.usage_repo.count_messages(days=30),
                "total_documents": await self.usage_repo.count_documents(days=30),
                "total_searches": await self.usage_repo.count_searches(days=30),
                "total_cost": await self.usage_repo.get_cost(days=30)
            },
            "weekly_breakdown": await self.get_daily_active_users(30),
            "top_users": await self.get_top_users("messages", 10),
            "source_breakdown": await self.get_source_usage(30),
            "trends": await self.get_usage_trends(30),
            "retention": await self._calculate_retention()
        }
        
        return report
    
    async def _calculate_retention(self) -> Dict[str, float]:
        """
        Calculate user retention rates
        """
        # Get users who signed up 30 days ago
        cohort_date = datetime.utcnow() - timedelta(days=30)
        cohort = await self.user_repo.get_users_by_signup_date(cohort_date)
        
        if not cohort:
            return {}
        
        total_cohort = len(cohort)
        
        # Calculate retention for different periods
        retention = {}
        
        for days in [1, 7, 14, 30]:
            active = await self.usage_repo.count_active_users_in_cohort(
                cohort,
                days_after=days
            )
            retention[f"day_{days}"] = (active / total_cohort) * 100 if total_cohort > 0 else 0
        
        return retention