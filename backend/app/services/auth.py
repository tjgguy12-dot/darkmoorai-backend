"""
Authentication Service
Handle user authentication, registration, and token management
"""

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import uuid
import secrets
from typing import Optional, Dict, Any

from app.config import config
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.token_repo import TokenRepository
from app.services.email import EmailService
from app.models.schemas import UserCreate, TokenResponse
from app.utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Authentication and authorization service
    """
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()
        self.email_service = EmailService()
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user
        """
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create user
        user = await self.user_repo.create({
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "role": "user",
            "is_active": True,
            "is_verified": False,
            "settings": {
                "theme": "light",
                "language": "en",
                "notifications_enabled": True
            }
        })
        
        # Create verification token
        verification_token = await self._create_verification_token(user["id"])
        
        # Send verification email
        await self.email_service.send_verification_email(
            email=user["email"],
            token=verification_token
        )
        
        logger.info(f"User registered: {user['id']}")
        
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user by email and password
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            return None
        
        if not user.get("is_active", True):
            logger.warning(f"Inactive user attempted login: {email}")
            return None
        
        if not pwd_context.verify(password, user["hashed_password"]):
            return None
        
        # Update last login
        await self.user_repo.update_last_login(user["id"])
        
        logger.info(f"User authenticated: {user['id']}")
        
        return user
    
    async def create_tokens(self, user: Dict[str, Any]) -> TokenResponse:
        """
        Create access and refresh tokens
        """
        # Access token (short-lived)
        access_token = self._create_access_token(user)
        
        # Refresh token (long-lived)
        refresh_token = await self._create_refresh_token(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=config.JWT_EXPIRES_IN
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        Get new access token using refresh token
        """
        # Verify refresh token
        token_data = await self.token_repo.get_refresh_token(refresh_token)
        
        if not token_data:
            return None
        
        # Check expiration
        if datetime.fromisoformat(token_data["expires_at"]) < datetime.utcnow():
            await self.token_repo.revoke_refresh_token(refresh_token)
            return None
        
        # Get user
        user = await self.user_repo.get(token_data["user_id"])
        
        if not user or not user.get("is_active", True):
            return None
        
        # Create new tokens
        return await self.create_tokens(user)
    
    async def logout_user(self, user_id: str):
        """
        Logout user (revoke all refresh tokens)
        """
        await self.token_repo.revoke_all_user_tokens(user_id)
        logger.info(f"User logged out: {user_id}")
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email with token
        """
        # Find token
        token_data = await self.token_repo.get_verification_token(token)
        
        if not token_data:
            return False
        
        # Check expiration
        if datetime.fromisoformat(token_data["expires_at"]) < datetime.utcnow():
            await self.token_repo.revoke_verification_token(token)
            return False
        
        # Update user
        await self.user_repo.update(token_data["user_id"], {
            "is_verified": True
        })
        
        # Revoke token
        await self.token_repo.revoke_verification_token(token)
        
        logger.info(f"Email verified for user: {token_data['user_id']}")
        
        return True
    
    async def send_password_reset_email(self, email: str):
        """
        Send password reset email
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            # Don't reveal if user exists
            return
        
        # Create reset token
        reset_token = await self._create_reset_token(user["id"])
        
        # Send email
        await self.email_service.send_password_reset_email(
            email=email,
            token=reset_token
        )
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password with token
        """
        # Find token
        token_data = await self.token_repo.get_reset_token(token)
        
        if not token_data:
            return False
        
        # Check expiration
        if datetime.fromisoformat(token_data["expires_at"]) < datetime.utcnow():
            await self.token_repo.revoke_reset_token(token)
            return False
        
        # Hash new password
        hashed_password = pwd_context.hash(new_password)
        
        # Update user
        await self.user_repo.update(token_data["user_id"], {
            "hashed_password": hashed_password
        })
        
        # Revoke token
        await self.token_repo.revoke_reset_token(token)
        
        # Revoke all refresh tokens for security
        await self.token_repo.revoke_all_user_tokens(token_data["user_id"])
        
        logger.info(f"Password reset for user: {token_data['user_id']}")
        
        return True
    
    def _create_access_token(self, user: Dict[str, Any]) -> str:
        """
        Create JWT access token
        """
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(seconds=config.JWT_EXPIRES_IN)
        }
        
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    async def _create_refresh_token(self, user: Dict[str, Any]) -> str:
        """
        Create refresh token (stored in DB)
        """
        token = secrets.token_urlsafe(32)
        
        await self.token_repo.create_refresh_token({
            "user_id": user["id"],
            "token": token,
            "expires_at": datetime.utcnow() + timedelta(days=30)
        })
        
        return token
    
    async def _create_verification_token(self, user_id: str) -> str:
        """
        Create email verification token
        """
        token = secrets.token_urlsafe(32)
        
        await self.token_repo.create_verification_token({
            "user_id": user_id,
            "token": token,
            "expires_at": datetime.utcnow() + timedelta(days=7)
        })
        
        return token
    
    async def _create_reset_token(self, user_id: str) -> str:
        """
        Create password reset token
        """
        token = secrets.token_urlsafe(32)
        
        await self.token_repo.create_reset_token({
            "user_id": user_id,
            "token": token,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        })
        
        return token
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        """
        user = await self.user_repo.get(user_id)
        
        if not user:
            return False
        
        if not pwd_context.verify(old_password, user["hashed_password"]):
            return False
        
        hashed_password = pwd_context.hash(new_password)
        
        await self.user_repo.update(user_id, {
            "hashed_password": hashed_password
        })
        
        # Revoke all refresh tokens
        await self.token_repo.revoke_all_user_tokens(user_id)
        
        logger.info(f"Password changed for user: {user_id}")
        
        return True