"""
Authentication Middleware
"""

from fastapi import Request, HTTPException
from typing import Optional

async def auth_middleware(request: Request, call_next):
    """Bypass auth for testing"""
    
    # Skip auth for public paths
    public_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/",
        "/api/v1/health",
        "/api/v1/auth"
    ]
    
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    # For testing, add a dummy user
    request.state.user = {
        "id": "test-user-123",
        "email": "test@darkmoor.ai",
        "username": "testuser",
        "role": "user"
    }
    
    return await call_next(request)