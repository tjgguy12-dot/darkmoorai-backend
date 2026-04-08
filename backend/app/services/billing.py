"""
Billing Service
Handle subscriptions, payments, and invoices
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import stripe

from app.config import config
from app.database.repositories.subscription_repo import SubscriptionRepository
from app.database.repositories.invoice_repo import InvoiceRepository
from app.database.repositories.user_repo import UserRepository
from app.utils.logger import logger

# Initialize Stripe
if config.STRIPE_SECRET_KEY:
    stripe.api_key = config.STRIPE_SECRET_KEY

class BillingService:
    """
    Subscription and billing service
    """
    
    def __init__(self):
        self.subscription_repo = SubscriptionRepository()
        self.invoice_repo = InvoiceRepository()
        self.user_repo = UserRepository()
    
    async def get_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current subscription
        """
        subscription = await self.subscription_repo.get_active_by_user(user_id)
        
        if not subscription:
            # Return default free tier
            return {
                "tier": "free",
                "status": "active",
                "messages_used": 0,
                "documents_used": 0,
                "tokens_used": 0,
                "limits": {
                    "messages_per_month": 100,
                    "documents": 5,
                    "max_file_size": 5 * 1024 * 1024,
                    "search_enabled": True
                }
            }
        
        return subscription
    
    async def create_subscription(
        self,
        user_id: str,
        tier: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new subscription
        """
        user = await self.user_repo.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Get or create Stripe customer
        if not user.get("stripe_customer_id"):
            customer = stripe.Customer.create(
                email=user["email"],
                metadata={"user_id": user_id}
            )
            await self.user_repo.update(user_id, {
                "stripe_customer_id": customer.id
            })
            customer_id = customer.id
        else:
            customer_id = user["stripe_customer_id"]
        
        # Attach payment method if provided
        if payment_method_id:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
        
        # Create subscription
        price_ids = {
            "pro": "price_pro_monthly",  # Replace with actual price ID
            "enterprise": "price_enterprise_monthly"
        }
        
        if tier not in price_ids:
            raise ValueError(f"Invalid tier: {tier}")
        
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_ids[tier]}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            metadata={"user_id": user_id}
        )
        
        # Store in database
        db_subscription = await self.subscription_repo.create({
            "user_id": user_id,
            "tier": tier,
            "status": "active",
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": subscription.id,
            "current_period_start": datetime.fromtimestamp(
                subscription.current_period_start
            ).isoformat(),
            "current_period_end": datetime.fromtimestamp(
                subscription.current_period_end
            ).isoformat()
        })
        
        logger.info(f"Subscription created for user {user_id}: {tier}")
        
        return db_subscription
    
    async def cancel_subscription(
        self,
        user_id: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel user's subscription
        """
        subscription = await self.subscription_repo.get_active_by_user(user_id)
        
        if not subscription or not subscription.get("stripe_subscription_id"):
            raise ValueError("No active subscription found")
        
        if immediate:
            # Cancel immediately
            stripe.Subscription.delete(subscription["stripe_subscription_id"])
            
            await self.subscription_repo.update(subscription["id"], {
                "status": "canceled"
            })
        else:
            # Cancel at period end
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=True
            )
            
            await self.subscription_repo.update(subscription["id"], {
                "cancel_at_period_end": True
            })
        
        logger.info(f"Subscription canceled for user {user_id}")
        
        return subscription
    
    async def reactivate_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Reactivate cancelled subscription
        """
        subscription = await self.subscription_repo.get_active_by_user(user_id)
        
        if not subscription or not subscription.get("stripe_subscription_id"):
            raise ValueError("No subscription found")
        
        # Remove cancel at period end
        stripe.Subscription.modify(
            subscription["stripe_subscription_id"],
            cancel_at_period_end=False
        )
        
        await self.subscription_repo.update(subscription["id"], {
            "cancel_at_period_end": False
        })
        
        logger.info(f"Subscription reactivated for user {user_id}")
        
        return subscription
    
    async def get_invoices(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user's invoices
        """
        return await self.invoice_repo.get_by_user(user_id, limit)
    
    async def get_invoice_pdf(self, user_id: str, invoice_id: str) -> Optional[str]:
        """
        Get invoice PDF URL
        """
        invoice = await self.invoice_repo.get(invoice_id)
        
        if not invoice or invoice["user_id"] != user_id:
            return None
        
        return invoice.get("invoice_pdf")
    
    async def get_payment_methods(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's payment methods
        """
        user = await self.user_repo.get(user_id)
        
        if not user or not user.get("stripe_customer_id"):
            return []
        
        payment_methods = stripe.PaymentMethod.list(
            customer=user["stripe_customer_id"],
            type="card"
        )
        
        return [{
            "id": pm.id,
            "brand": pm.card.brand,
            "last4": pm.card.last4,
            "exp_month": pm.card.exp_month,
            "exp_year": pm.card.exp_year,
            "is_default": pm.id == user.get("default_payment_method")
        } for pm in payment_methods.data]
    
    async def add_payment_method(
        self,
        user_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Add payment method to user
        """
        user = await self.user_repo.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        if not user.get("stripe_customer_id"):
            customer = stripe.Customer.create(
                email=user["email"],
                metadata={"user_id": user_id}
            )
            customer_id = customer.id
            await self.user_repo.update(user_id, {
                "stripe_customer_id": customer_id
            })
        else:
            customer_id = user["stripe_customer_id"]
        
        # Attach payment method
        payment_method = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
        
        # Set as default if it's the first one
        methods = await self.get_payment_methods(user_id)
        if len(methods) == 1:
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            await self.user_repo.update(user_id, {
                "default_payment_method": payment_method_id
            })
        
        return {
            "id": payment_method.id,
            "brand": payment_method.card.brand,
            "last4": payment_method.card.last4,
            "exp_month": payment_method.card.exp_month,
            "exp_year": payment_method.card.exp_year
        }
    
    async def remove_payment_method(self, user_id: str, method_id: str):
        """
        Remove payment method
        """
        user = await self.user_repo.get(user_id)
        
        if not user or not user.get("stripe_customer_id"):
            return
        
        # Detach from Stripe
        stripe.PaymentMethod.detach(method_id)
        
        # Update default if needed
        if user.get("default_payment_method") == method_id:
            await self.user_repo.update(user_id, {
                "default_payment_method": None
            })
    
    async def set_default_payment_method(self, user_id: str, method_id: str):
        """
        Set default payment method
        """
        user = await self.user_repo.get(user_id)
        
        if not user or not user.get("stripe_customer_id"):
            raise ValueError("User has no Stripe customer")
        
        stripe.Customer.modify(
            user["stripe_customer_id"],
            invoice_settings={
                "default_payment_method": method_id
            }
        )
        
        await self.user_repo.update(user_id, {
            "default_payment_method": method_id
        })
    
    async def get_current_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get current billing period usage
        """
        subscription = await self.subscription_repo.get_active_by_user(user_id)
        
        if not subscription:
            return {
                "messages_used": 0,
                "documents_used": 0,
                "tokens_used": 0,
                "cost": 0
            }
        
        return {
            "messages_used": subscription.get("messages_used", 0),
            "documents_used": subscription.get("documents_used", 0),
            "tokens_used": subscription.get("tokens_used", 0),
            "cost": subscription.get("total_cost", 0)
        }
    
    # Webhook handlers
    
    async def handle_subscription_created(self, data: Dict[str, Any]):
        """Handle subscription.created webhook"""
        logger.info(f"Subscription created: {data['id']}")
    
    async def handle_subscription_updated(self, data: Dict[str, Any]):
        """Handle subscription.updated webhook"""
        logger.info(f"Subscription updated: {data['id']}")
        
        # Update in database
        subscription_id = data["id"]
        status = data["status"]
        cancel_at_period_end = data.get("cancel_at_period_end", False)
        
        await self.subscription_repo.update_by_stripe_id(
            subscription_id,
            {
                "status": status,
                "cancel_at_period_end": cancel_at_period_end
            }
        )
    
    async def handle_subscription_deleted(self, data: Dict[str, Any]):
        """Handle subscription.deleted webhook"""
        logger.info(f"Subscription deleted: {data['id']}")
        
        subscription_id = data["id"]
        await self.subscription_repo.update_by_stripe_id(
            subscription_id,
            {"status": "canceled"}
        )
    
    async def handle_payment_succeeded(self, data: Dict[str, Any]):
        """Handle invoice.payment_succeeded webhook"""
        logger.info(f"Payment succeeded: {data['id']}")
        
        # Create invoice record
        await self.invoice_repo.create({
            "stripe_invoice_id": data["id"],
            "subscription_id": data.get("subscription"),
            "amount": data["amount_paid"],
            "currency": data["currency"],
            "status": "paid",
            "invoice_pdf": data.get("invoice_pdf"),
            "hosted_invoice_url": data.get("hosted_invoice_url")
        })
    
    async def handle_payment_failed(self, data: Dict[str, Any]):
        """Handle invoice.payment_failed webhook"""
        logger.warning(f"Payment failed: {data['id']}")
        
        # Update subscription status
        subscription_id = data.get("subscription")
        if subscription_id:
            await self.subscription_repo.update_by_stripe_id(
                subscription_id,
                {"status": "past_due"}
            )
    
    async def handle_payment_method_attached(self, data: Dict[str, Any]):
        """Handle payment_method.attached webhook"""
        logger.info(f"Payment method attached: {data['id']}")
    
    async def handle_refund(self, data: Dict[str, Any]):
        """Handle charge.refunded webhook"""
        logger.info(f"Refund processed: {data['id']}")