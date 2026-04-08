"""
API Key Repository
Database operations for API keys
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from app.database.repositories.base_repo import BaseRepository
from app.models.subscription import ApiKey

class ApiKeyRepository(BaseRepository):
    """
    API key repository with key-specific queries
    """
    
    def __init__(self):
        super().__init__(ApiKey)
    
    async def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get API key by key string
        """
        keys = await self.get_many(key=key)
        return keys[0] if keys else None
    
    async def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all API keys for a user
        """
        return await self.get_many(user_id=user_id)
    
    async def update_last_used(self, key_id: str):
        """
        Update last used timestamp
        """
        await self.update(key_id, {
            "last_used_at": datetime.utcnow().isoformat()
        })
    
    async def revoke(self, key_id: str):
        """
        Revoke API key
        """
        await self.delete(key_id)
    
    async def revoke_by_user(self, user_id: str):
        """
        Revoke all API keys for a user
        """
        keys = await self.get_by_user(user_id)
        for key in keys:
            await self.delete(key["id"])
    
    async def delete_by_user(self, user_id: str):
        """
        Delete all API keys for a user
        """
        await self.revoke_by_user(user_id)