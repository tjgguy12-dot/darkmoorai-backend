"""
Usage Model
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Index, DateTime
from datetime import datetime

from app.models.database import BaseModel


class UsageEvent(BaseModel):
    __tablename__ = "usage_events"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event = Column(String, nullable=False)
    properties = Column(JSON, default={})
    
    __table_args__ = (
        Index('idx_usage_user_event', user_id, event),
        Index('idx_usage_created', "created_at"),
    )