"""
OTP Model for Email Verification
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from datetime import datetime, timedelta
import uuid

from app.models.database import BaseModel


class OTP(BaseModel):
    __tablename__ = "otps"
    
    email = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=0)
    
    @classmethod
    def create_for_email(cls, email: str, code: str, expiry_minutes: int = 10):
        """Create a new OTP for an email"""
        return cls(
            email=email,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
    
    def is_valid(self) -> bool:
        """Check if OTP is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def mark_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.updated_at = datetime.utcnow()
    
    def increment_attempts(self):
        """Increment failed attempt counter"""
        self.attempt_count += 1
        self.updated_at = datetime.utcnow()