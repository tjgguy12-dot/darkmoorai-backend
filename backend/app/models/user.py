"""
User Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Float
from datetime import datetime

from app.models.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)          # Added for login tracking
    settings = Column(JSON, default={})
    preferences = Column(JSON, default={})
    total_messages = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Optional relationships (uncomment if you have them)
    # conversations = relationship("Conversation", back_populates="user")
    # documents = relationship("Document", back_populates="user")