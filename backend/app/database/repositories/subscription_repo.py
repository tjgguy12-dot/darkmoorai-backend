"""
Subscription Repository
Database operations for subscriptions
"""

from typing import Optional, Dict, Any

from app.database.repositories.base_repo import BaseRepository
from app.models.subscription import Subscription

class SubscriptionRepository(BaseRepository):
    """
    Subscription repository with subscription-specific queries
    """
    
    def __init__(self):
        super().__init__(Subscription)
    
    async def get_active_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get active subscription for user
        """
        subscriptions = await self.get_many(
            user_id=user_id,
            status="active"
        )
        
        if subscriptions:
            return sorted(subscriptions, key=lambda x: x["created_at"], reverse=True)[0]
        
        return None
    
    async def get_by_stripe_id(self, stripe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription by Stripe ID
        """
        subs = await self.get_many(stripe_subscription_id=stripe_id)
        return subs[0] if subs else None
    
    async def update_by_stripe_id(self, stripe_id: str, updates: Dict[str, Any]):
        """
        Update subscription by Stripe ID
        """
        sub = await self.get_by_stripe_id(stripe_id)
        if sub:
            await self.update(sub["id"], updates)
    
    async def increment_usage(self, subscription_id: str, messages: int = 0, documents: int = 0, tokens: int = 0):
        """
        Increment usage counters
        """
        sub = await self.get(subscription_id)
        if sub:
            await self.update(subscription_id, {
                "messages_used": sub.get("messages_used", 0) + messages,
                "documents_used": sub.get("documents_used", 0) + documents,
                "tokens_used": sub.get("tokens_used", 0) + tokens
            })