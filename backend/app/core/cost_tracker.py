"""
Cost Tracker Module
Track and limit API costs per user
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from app.core.cache import Cache
from app.config import config
from app.utils.logger import logger

class CostTracker:
    """
    Track API costs per user with daily budgets
    """
    
    def __init__(self):
        self.cache = Cache()
        self.daily_budget = config.DAILY_BUDGET_PER_USER
    
    async def track_usage(
        self,
        user_id: str,
        cost: float,
        tokens: int,
        action: str = "api_call"
    ):
        """
        Track cost for a user action
        """
        today = datetime.utcnow().date().isoformat()
        
        # Daily total
        daily_key = f"cost:daily:{user_id}:{today}"
        await self.cache.incrbyfloat(daily_key, cost)
        await self.cache.expire(daily_key, 86400 * 2)  # 2 days
        
        # Monthly total
        month_key = f"cost:monthly:{user_id}:{today[:7]}"  # YYYY-MM
        await self.cache.incrbyfloat(month_key, cost)
        await self.cache.expire(month_key, 86400 * 35)  # 35 days
        
        # Token tracking
        token_key = f"tokens:{user_id}:{today}"
        await self.cache.incr(token_key, tokens)
        await self.cache.expire(token_key, 86400 * 2)
        
        # Action tracking
        action_key = f"actions:{user_id}:{today}:{action}"
        await self.cache.incr(action_key, 1)
        await self.cache.expire(action_key, 86400 * 2)
        
        # Check if approaching limit
        daily_total = await self.cache.get(daily_key) or 0
        if daily_total > self.daily_budget * 0.8:
            logger.warning(f"User {user_id} at {(daily_total/self.daily_budget)*100:.1f}% of daily budget")
    
    async def check_budget(self, user_id: str) -> bool:
        """
        Check if user has budget remaining
        """
        # Admin users have unlimited budget
        if await self._is_admin(user_id):
            return True
        
        today = datetime.utcnow().date().isoformat()
        daily_key = f"cost:daily:{user_id}:{today}"
        
        daily_total = await self.cache.get(daily_key) or 0
        
        if daily_total >= self.daily_budget:
            logger.info(f"User {user_id} has exceeded daily budget (${daily_total:.4f} / ${self.daily_budget:.2f})")
            return False
        
        return True
    
    async def get_daily_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's daily usage
        """
        today = datetime.utcnow().date().isoformat()
        daily_key = f"cost:daily:{user_id}:{today}"
        
        cost = await self.cache.get(daily_key) or 0
        remaining = max(0, self.daily_budget - cost)
        
        return {
            "date": today,
            "cost": round(cost, 6),
            "budget": self.daily_budget,
            "remaining": round(remaining, 6),
            "percentage": round((cost / self.daily_budget) * 100, 2) if self.daily_budget > 0 else 0
        }
    
    async def get_monthly_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's monthly usage
        """
        today = datetime.utcnow()
        month_key = f"cost:monthly:{user_id}:{today.strftime('%Y-%m')}"
        
        cost = await self.cache.get(month_key) or 0
        
        # Calculate days in month
        next_month = today.replace(day=28) + timedelta(days=4)
        days_in_month = (next_month - timedelta(days=next_month.day)).day
        
        # Projected monthly cost
        day_of_month = today.day
        projected = (cost / day_of_month) * days_in_month if day_of_month > 0 else 0
        
        return {
            "month": today.strftime("%Y-%m"),
            "cost": round(cost, 6),
            "projected": round(projected, 6),
            "days_used": today.day,
            "days_in_month": days_in_month
        }
    
    async def get_user_stats(self, user_id: str, period: str = "month") -> Dict[str, Any]:
        """
        Get comprehensive user usage stats
        """
        daily = await self.get_daily_usage(user_id)
        monthly = await self.get_monthly_usage(user_id)
        
        # Get token usage
        today = datetime.utcnow().date().isoformat()
        token_key = f"tokens:{user_id}:{today}"
        tokens_today = await self.cache.get(token_key) or 0
        
        # Get action counts
        actions = {}
        action_pattern = f"actions:{user_id}:{today}:*"
        # In production, scan for action keys
        
        return {
            "user_id": user_id,
            "daily": daily,
            "monthly": monthly,
            "tokens_today": tokens_today,
            "actions_today": actions,
            "budget_remaining": daily["remaining"] > 0
        }
    
    async def get_today_total_cost(self) -> float:
        """
        Get total cost for today across all users
        """
        # In production, aggregate from database
        # This is a simplified version
        today = datetime.utcnow().date().isoformat()
        pattern = f"cost:daily:*:{today}"
        
        total = 0.0
        # Scan for keys and sum
        # Simplified for example
        
        return total
    
    async def get_month_total_cost(self) -> float:
        """
        Get total cost for current month
        """
        today = datetime.utcnow()
        month = today.strftime('%Y-%m')
        pattern = f"cost:monthly:*:{month}"
        
        total = 0.0
        # Scan for keys and sum
        
        return total
    
    async def _is_admin(self, user_id: str) -> bool:
        """
        Check if user is admin
        """
        # In production, check database
        admin_ids = ["admin1", "admin2"]  # Example
        return user_id in admin_ids
    
    async def reset_daily_budget(self, user_id: str):
        """
        Reset daily budget (for testing/admin)
        """
        today = datetime.utcnow().date().isoformat()
        daily_key = f"cost:daily:{user_id}:{today}"
        await self.cache.delete(daily_key)
        logger.info(f"Daily budget reset for user {user_id}")

# Global instance
cost_tracker = CostTracker()