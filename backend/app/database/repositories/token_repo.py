"""
Token Repository
Database operations for authentication tokens
"""

from typing import Optional, Dict, Any

from app.database.repositories.base_repo import BaseRepository
from app.models.token import RefreshToken, VerificationToken, ResetToken

class TokenRepository:
    """
    Token repository for all token types
    """
    
    def __init__(self):
        self.refresh_repo = RefreshTokenRepository()
        self.verification_repo = VerificationTokenRepository()
        self.reset_repo = ResetTokenRepository()
    
    async def create_refresh_token(self, data: Dict[str, Any]):
        return await self.refresh_repo.create(data)
    
    async def get_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        return await self.refresh_repo.get_by_token(token)
    
    async def revoke_refresh_token(self, token: str):
        await self.refresh_repo.revoke(token)
    
    async def revoke_all_user_tokens(self, user_id: str):
        await self.refresh_repo.revoke_by_user(user_id)
    
    async def create_verification_token(self, data: Dict[str, Any]):
        return await self.verification_repo.create(data)
    
    async def get_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        return await self.verification_repo.get_by_token(token)
    
    async def revoke_verification_token(self, token: str):
        await self.verification_repo.revoke(token)
    
    async def create_reset_token(self, data: Dict[str, Any]):
        return await self.reset_repo.create(data)
    
    async def get_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        return await self.reset_repo.get_by_token(token)
    
    async def revoke_reset_token(self, token: str):
        await self.reset_repo.revoke(token)

class RefreshTokenRepository(BaseRepository):
    """Refresh token repository"""
    
    def __init__(self):
        from app.models.token import RefreshToken
        super().__init__(RefreshToken)
    
    async def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        tokens = await self.get_many(token=token)
        return tokens[0] if tokens else None
    
    async def revoke(self, token: str):
        token_data = await self.get_by_token(token)
        if token_data:
            await self.delete(token_data["id"])
    
    async def revoke_by_user(self, user_id: str):
        tokens = await self.get_many(user_id=user_id)
        for token in tokens:
            await self.delete(token["id"])

class VerificationTokenRepository(BaseRepository):
    """Email verification token repository"""
    
    def __init__(self):
        from app.models.token import VerificationToken
        super().__init__(VerificationToken)
    
    async def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        tokens = await self.get_many(token=token)
        return tokens[0] if tokens else None
    
    async def revoke(self, token: str):
        token_data = await self.get_by_token(token)
        if token_data:
            await self.delete(token_data["id"])

class ResetTokenRepository(BaseRepository):
    """Password reset token repository"""
    
    def __init__(self):
        from app.models.token import ResetToken
        super().__init__(ResetToken)
    
    async def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        tokens = await self.get_many(token=token)
        return tokens[0] if tokens else None
    
    async def revoke(self, token: str):
        token_data = await self.get_by_token(token)
        if token_data:
            await self.delete(token_data["id"])