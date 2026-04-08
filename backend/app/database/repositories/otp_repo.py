"""
OTP Repository
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.database.repositories.base_repo import BaseRepository
from app.models.otp import OTP


class OTPRepository(BaseRepository):
    """OTP repository with OTP-specific queries"""
    
    def __init__(self):
        super().__init__(OTP)
    
    async def get_valid_otp(self, email: str, code: str) -> Optional[Dict[str, Any]]:
        """Get a valid (unused, not expired) OTP for an email"""
        from sqlalchemy import select, and_
        from app.database.session import async_session_maker
        
        async with async_session_maker() as session:
            stmt = select(OTP).where(
                and_(
                    OTP.email == email,
                    OTP.code == code,
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow()
                )
            )
            result = await session.execute(stmt)
            otp = result.scalar_one_or_none()
            
            if otp:
                return otp.to_dict()
            return None
    
    async def mark_otp_used(self, otp_id: str):
        """Mark an OTP as used"""
        await self.update(otp_id, {"is_used": True})
    
    async def increment_attempts(self, otp_id: str):
        """Increment failed attempt counter"""
        otp = await self.get(otp_id)
        if otp:
            await self.update(otp_id, {"attempt_count": otp.get("attempt_count", 0) + 1})
    
    async def invalidate_old_otps(self, email: str):
        """Invalidate all unused OTPs for an email"""
        from sqlalchemy import update
        from app.database.session import async_session_maker
        
        async with async_session_maker() as session:
            stmt = update(OTP).where(
                OTP.email == email,
                OTP.is_used == False
            ).values(is_used=True)
            await session.execute(stmt)
            await session.commit()