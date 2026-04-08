"""
Rate Limit Dependencies
Check rate limits for specific endpoints
"""

from fastapi import HTTPException, Request
from typing import Optional
import time

from app.core.cache import cache
from app.config import config

async def rate_limit(request: Request, requests: int = 60, period: int = 60) -> bool:
    """
    Check rate limit for request
    """
    if not config.RATE_LIMIT_ENABLED:
        return True
    
    # Get client identifier
    client_id = await get_client_id(request)
    
    # Create key
    key = f"ratelimit:{client_id}:{request.url.path}"
    
    # Get current count
    current = await cache.get(key) or 0
    
    if current >= requests:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Increment count
    await cache.set(key, current + 1, ttl=period)
    
    return True

async def get_client_id(request: Request) -> str:
    """
    Get unique client identifier
    """
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.get('id', 'unknown')}"
    
    return f"ip:{request.client.host if request.client else 'unknown'}"

# Pre-configured rate limiters
async def rate_limit_chat(request: Request):
    """30 requests per minute for chat"""
    return await rate_limit(request, requests=30, period=60)

async def rate_limit_search(request: Request):
    """20 requests per minute for search"""
    return await rate_limit(request, requests=20, period=60)

async def rate_limit_upload(request: Request):
    """10 requests per minute for upload"""
    return await rate_limit(request, requests=10, period=60)

async def rate_limit_default(request: Request):
    """60 requests per minute default"""
    return await rate_limit(request, requests=60, period=60)