"""
Conversation Models
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.database import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    settings = Column(JSON, default={})
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_conversation_user_created', user_id, "created_at"),
    )


class Message(BaseModel):
    __tablename__ = "messages"
    
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    
    tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    sources = Column(JSON, default=[])
    extra_data = Column(JSON, default={})
    
    feedback_rating = Column(Integer)
    feedback_text = Column(String)
    
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index('idx_message_conversation_created', conversation_id, "created_at"),
    )