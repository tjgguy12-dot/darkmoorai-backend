"""
User Service
Handle user profile and settings management
"""

from typing import Optional, Dict, Any, List
import shutil
from pathlib import Path
import secrets
from datetime import datetime, timedelta

from app.database.repositories.user_repo import UserRepository
from app.database.repositories.document_repo import DocumentRepository
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.api_key_repo import ApiKeyRepository
from app.services.email import EmailService
from app.config import config
from app.utils.logger import logger

class UserService:
    """
    User profile and settings service
    """
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.document_repo = DocumentRepository()
        self.conversation_repo = ConversationRepository()
        self.api_key_repo = ApiKeyRepository()
        self.email_service = EmailService()
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile
        """
        return await self.user_repo.get(user_id)
    
    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile
        """
        # Remove fields that can't be updated
        allowed_updates = ["full_name", "avatar_url", "settings"]
        filtered_updates = {
            k: v for k, v in updates.items()
            if k in allowed_updates and v is not None
        }
        
        if filtered_updates:
            await self.user_repo.update(user_id, filtered_updates)
        
        return await self.user_repo.get(user_id)
    
    async def save_avatar(self, user_id: str, file) -> str:
        """
        Save user avatar
        """
        # Create avatars directory
        avatar_dir = Path("data/avatars")
        avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        extension = Path(file.filename).suffix
        avatar_path = avatar_dir / f"{user_id}{extension}"
        
        with open(avatar_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Update user
        avatar_url = f"/avatars/{user_id}{extension}"
        await self.user_repo.update(user_id, {"avatar_url": avatar_url})
        
        return avatar_url
    
    async def get_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get user settings
        """
        user = await self.user_repo.get(user_id)
        return user.get("settings", {})
    
    async def update_settings(
        self,
        user_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user settings
        """
        current = await self.get_settings(user_id)
        current.update(settings)
        
        await self.user_repo.update(user_id, {"settings": current})
        
        return current
    
    async def get_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's API keys
        """
        return await self.api_key_repo.get_by_user(user_id)
    
    async def create_api_key(self, user_id: str, name: str) -> Dict[str, Any]:
        """
        Create new API key
        """
        # Generate key
        key = f"dm_{secrets.token_urlsafe(32)}"
        key_preview = key[-4:]
        
        # Get user's subscription for limits
        # Simplified: default to 30 days
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        api_key = await self.api_key_repo.create({
            "user_id": user_id,
            "name": name,
            "key": key,
            "key_preview": key_preview,
            "expires_at": expires_at.isoformat(),
            "permissions": ["read", "chat"]
        })
        
        logger.info(f"API key created for user {user_id}: {name}")
        
        return api_key
    
    async def delete_api_key(self, user_id: str, key_id: str):
        """
        Delete API key
        """
        # Verify ownership
        key = await self.api_key_repo.get(key_id)
        
        if key and key["user_id"] == user_id:
            await self.api_key_repo.delete(key_id)
            logger.info(f"API key {key_id} deleted for user {user_id}")
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data (GDPR compliance)
        """
        user = await self.user_repo.get(user_id)
        documents = await self.document_repo.get_by_user(user_id)
        conversations = await self.conversation_repo.get_by_user(user_id)
        api_keys = await self.api_key_repo.get_by_user(user_id)
        
        # Remove sensitive data
        if user:
            user.pop("hashed_password", None)
        
        return {
            "user": user,
            "documents": documents,
            "conversations": conversations,
            "api_keys": [
                {k: v for k, v in key.items() if k != "key"}
                for key in api_keys
            ],
            "exported_at": datetime.utcnow().isoformat()
        }
    
    async def delete_exported_data(self, user_id: str):
        """
        Delete exported data files
        """
        # Implementation depends on export storage
        logger.info(f"Exported data deleted for user {user_id}")
    
    async def get_notification_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get notification preferences
        """
        settings = await self.get_settings(user_id)
        return settings.get("notifications", {
            "email": True,
            "push": False,
            "marketing": False
        })
    
    async def update_notification_settings(
        self,
        user_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update notification preferences
        """
        current = await self.get_settings(user_id)
        
        if "notifications" not in current:
            current["notifications"] = {}
        
        current["notifications"].update(settings)
        
        await self.update_settings(user_id, current)
        
        return current["notifications"]
    
    async def delete_account(self, user_id: str):
        """
        Delete user account and all data
        """
        # Delete all user data
        await self.document_repo.delete_by_user(user_id)
        await self.conversation_repo.delete_by_user(user_id)
        await self.api_key_repo.delete_by_user(user_id)
        
        # Delete user
        await self.user_repo.delete(user_id)
        
        logger.info(f"Account deleted for user {user_id}")
    
    async def mark_email_bounced(self, email: str):
        """
        Mark email as bounced
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            await self.user_repo.update(user["id"], {
                "email_bounced": True,
                "bounced_at": datetime.utcnow().isoformat()
            })
    
    async def mark_spam_reported(self, email: str):
        """
        Mark email as spam
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            await self.user_repo.update(user["id"], {
                "marked_spam": True,
                "spam_reported_at": datetime.utcnow().isoformat()
            })
    
    async def process_unsubscribe(self, email: str):
        """
        Process unsubscribe request
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            settings = await self.get_settings(user["id"])
            settings.setdefault("notifications", {})["marketing"] = False
            await self.update_settings(user["id"], settings)