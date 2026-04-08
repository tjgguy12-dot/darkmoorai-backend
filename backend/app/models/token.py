"""
Token Models
Authentication tokens (refresh, verification, reset)
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from datetime import datetime

from app.models.database import BaseModel

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class VerificationToken(BaseModel):
    __tablename__ = "verification_tokens"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class ResetToken(BaseModel):
    __tablename__ = "reset_tokens"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)