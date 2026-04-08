"""
Authentication Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import time

from app.config import config

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user"""
    
    # For testing without token, return a test user
    if not credentials:
        return {
            "id": "test-user-123",
            "email": "test@darkmoor.ai",
            "username": "testuser",
            "role": "user",
            "is_active": True
        }
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM]
        )
        
        return {
            "id": payload.get("sub", "test-user"),
            "email": payload.get("email", "test@darkmoor.ai"),
            "username": "testuser",
            "role": "user",
            "is_active": True
        }
        
    except JWTError:
        # Return test user for now
        return {
            "id": "test-user-123",
            "email": "test@darkmoor.ai",
            "username": "testuser",
            "role": "user",
            "is_active": True
        }


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Get admin user"""
    return current_user