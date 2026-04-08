"""
Invoice Repository
Database operations for invoices
"""

from typing import List, Dict, Any, Optional

from app.database.repositories.base_repo import BaseRepository
from app.models.subscription import Invoice

class InvoiceRepository(BaseRepository):
    """
    Invoice repository with invoice-specific queries
    """
    
    def __init__(self):
        super().__init__(Invoice)
    
    async def get_by_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get invoices by user (via subscription)
        """
        from .subscription_repo import SubscriptionRepository
        
        sub_repo = SubscriptionRepository()
        subscriptions = await sub_repo.get_many(user_id=user_id)
        
        if not subscriptions:
            return []
        
        sub_ids = [s["id"] for s in subscriptions]
        
        # Simplified - get invoices for each subscription
        all_invoices = []
        for sub_id in sub_ids:
            invoices = await self.get_many(subscription_id=sub_id, limit=limit)
            all_invoices.extend(invoices)
        
        return sorted(all_invoices, key=lambda x: x["created_at"], reverse=True)[:limit]
    
    async def get_by_stripe_id(self, stripe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invoice by Stripe ID
        """
        invoices = await self.get_many(stripe_invoice_id=stripe_id)
        return invoices[0] if invoices else None