"""
Subscription Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.database import BaseModel


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    
    message_limit = Column(Integer)
    document_limit = Column(Integer)
    token_limit = Column(Integer)
    
    messages_used = Column(Integer, default=0)
    documents_used = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    
    current_period_start = Column(String)
    current_period_end = Column(String)
    cancel_at_period_end = Column(Boolean, default=False)
    
    extra_data = Column(JSON, default={})
    
    user = relationship("User", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="subscription", cascade="all, delete-orphan")


class Invoice(BaseModel):
    __tablename__ = "invoices"
    
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    stripe_invoice_id = Column(String, unique=True)
    
    amount = Column(Integer)
    currency = Column(String, default="usd")
    status = Column(String)
    
    invoice_pdf = Column(String)
    hosted_invoice_url = Column(String)
    
    extra_data = Column(JSON, default={})
    
    subscription = relationship("Subscription", back_populates="invoices")


class ApiKey(BaseModel):
    __tablename__ = "api_keys"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    
    name = Column(String)
    key = Column(String, unique=True, index=True)
    key_preview = Column(String)
    
    expires_at = Column(String)
    last_used_at = Column(String)
    
    permissions = Column(JSON, default=["read"])
    extra_data = Column(JSON, default={})
    
    user = relationship("User", back_populates="api_keys")
    subscription = relationship("Subscription", back_populates="api_keys")