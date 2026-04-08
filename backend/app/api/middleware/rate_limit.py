"""
Rate Limiting Middleware
Prevent abuse by limiting request frequency
"""

from fastapi import Request, HTTPException
from typing import Optional
import time
import hashlib

from app.core.cache import Cache
from app.config import config
from app.utils.logger import logger

cache = Cache()

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    """
    if not config.RATE_LIMIT_ENABLED:
        return await call_next(request)
    
    # Skip rate limiting for health checks
    if request.url.path.startswith("/api/v1/health"):
        return await call_next(request)
    
    # Get client identifier (user ID or IP)
    client_id = await get_client_id(request)
    
    # Check rate limit
    if await is_rate_limited(client_id, request.method, request.url.path):
        logger.warning(f"Rate limit exceeded for {client_id}")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = await get_remaining_requests(client_id)
    response.headers["X-RateLimit-Limit"] = str(config.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + config.RATE_LIMIT_PERIOD))
    
    return response

async def get_client_id(request: Request) -> str:
    """
    Get unique client identifier
    """
    # Use user ID if authenticated
    if hasattr(request.state, "user"):
        return f"user:{request.state.user['id']}"
    
    # Otherwise use IP + User-Agent
    ip = request.client.host
    ua = request.headers.get("User-Agent", "")
    client_id = f"anon:{ip}:{ua}"
    
    # Hash to avoid long strings
    return hashlib.md5(client_id.encode()).hexdigest()

async def is_rate_limited(client_id: str, method: str, path: str) -> bool:
    """
    Check if client is rate limited
    """
    # Different limits for different endpoints
    limits = {
        "chat": 30,      # 30 requests per minute
        "search": 20,    # 20 searches per minute
        "upload": 10,    # 10 uploads per minute
        "default": 60    # 60 other requests
    }
    
    # Determine endpoint type
    if "/chat" in path:
        limit = limits["chat"]
        key = f"ratelimit:{client_id}:chat"
    elif "/search" in path:
        limit = limits["search"]
        key = f"ratelimit:{client_id}:search"
    elif "/documents" in path and method == "POST":
        limit = limits["upload"]
        key = f"ratelimit:{client_id}:upload"
    else:
        limit = limits["default"]
        key = f"ratelimit:{client_id}:default"
    
    # Get current count
    count = await cache.get(key) or 0
    
    if count >= limit:
        return True
    
    # Increment count
    await cache.incr(key, 1)
    await cache.expire(key, config.RATE_LIMIT_PERIOD)
    
    return False

async def get_remaining_requests(client_id: str) -> int:
    """
    Get remaining requests for client
    """
    key = f"ratelimit:{client_id}:default"
    count = await cache.get(key) or 0
    return max(0, config.RATE_LIMIT_REQUESTS - count)