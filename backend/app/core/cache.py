"""
Cache Module - Complete with Redis and Memory Cache
"""

import json
import pickle
import hashlib
import asyncio
from typing import Any, Optional, Union, Dict
from datetime import timedelta
import redis.asyncio as redis
import os

from app.config import config
from app.utils.logger import logger


class Cache:
    """Distributed cache with Redis backend and memory fallback"""
    
    def __init__(self):
        self.redis = None
        self.memory_cache = {}
        self.memory_ttl = {}
        self.use_redis = False
    
    async def init(self):
        """Initialize cache connection – uses REDIS_URL from env or config"""
        redis_url = os.getenv("REDIS_URL", config.REDIS_URL)
        
        if redis_url:
            try:
                self.redis = redis.from_url(
                    redis_url,
                    decode_responses=False,
                    encoding=None
                )
                await self.redis.ping()
                self.use_redis = True
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis unavailable, using memory cache: {e}")
                self.use_redis = False
        else:
            logger.info("No Redis URL configured, using memory cache")
            self.use_redis = False
    
    async def close(self):
        """Close cache connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if self.use_redis:
            try:
                data = await self.redis.get(key)
                if data:
                    return pickle.loads(data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                self.use_redis = False
        
        # Memory cache fallback
        if key in self.memory_cache:
            if key in self.memory_ttl:
                if asyncio.get_event_loop().time() > self.memory_ttl[key]:
                    del self.memory_cache[key]
                    del self.memory_ttl[key]
                    return default
            return self.memory_cache[key]
        
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None,
        nx: bool = False
    ) -> bool:
        """Set value in cache"""
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        
        data = pickle.dumps(value)
        
        if self.use_redis:
            try:
                if nx:
                    result = await self.redis.set(key, data, nx=True, ex=ttl)
                else:
                    result = await self.redis.set(key, data, ex=ttl)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                self.use_redis = False
        
        self.memory_cache[key] = value
        if ttl:
            self.memory_ttl[key] = asyncio.get_event_loop().time() + ttl
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if self.use_redis:
            try:
                result = await self.redis.delete(key)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if key in self.memory_cache:
            del self.memory_cache[key]
            if key in self.memory_ttl:
                del self.memory_ttl[key]
            return True
        
        return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment integer counter"""
        if self.use_redis:
            try:
                return await self.redis.incr(key, amount)
            except Exception as e:
                logger.error(f"Redis incr error: {e}")
                self.use_redis = False
        
        # Memory fallback
        if key not in self.memory_cache:
            self.memory_cache[key] = 0
        self.memory_cache[key] += amount
        return self.memory_cache[key]
    
    async def incrbyfloat(self, key: str, amount: float = 1.0) -> float:
        """Increment float counter (for cost tracking)"""
        if self.use_redis:
            try:
                return await self.redis.incrbyfloat(key, amount)
            except Exception as e:
                logger.error(f"Redis incrbyfloat error: {e}")
                self.use_redis = False
        
        # Memory fallback
        if key not in self.memory_cache:
            self.memory_cache[key] = 0.0
        self.memory_cache[key] += amount
        return self.memory_cache[key]
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        if self.use_redis:
            try:
                return await self.redis.expire(key, seconds)
            except Exception as e:
                logger.error(f"Redis expire error: {e}")
                self.use_redis = False
        
        # Memory fallback
        if key in self.memory_cache:
            self.memory_ttl[key] = asyncio.get_event_loop().time() + seconds
            return True
        
        return False
    
    async def clear_pattern(self, pattern: str):
        """Clear keys matching pattern (Redis only)"""
        if self.use_redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.error(f"Redis clear pattern error: {e}")


# Create global cache instance
cache = Cache()


# ============================================================================
# Helper functions for main.py
# ============================================================================

async def init_cache():
    """Initialize cache for application startup"""
    await cache.init()


async def close_cache():
    """Close cache for application shutdown"""
    await cache.close()


async def get_cached(key: str, default: Any = None) -> Any:
    """Get cached value"""
    return await cache.get(key, default)


async def set_cached(key: str, value: Any, ttl: Optional[int] = None):
    """Set cached value"""
    await cache.set(key, value, ttl)


async def delete_cached(key: str):
    """Delete cached value"""
    await cache.delete(key)


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# ============================================================================
# Health check functions
# ============================================================================

async def check_redis_connection() -> Dict[str, Any]:
    """Check Redis connection health"""
    try:
        if cache.use_redis:
            await cache.redis.ping()
            return {
                "healthy": True,
                "message": "Redis connection successful",
                "type": "redis"
            }
        else:
            return {
                "healthy": True,
                "message": "Using memory cache (Redis not configured)",
                "type": "memory"
            }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Redis connection failed"
        }


async def check_db_connection() -> Dict[str, Any]:
    """Check database connection health - simplified"""
    try:
        # Try to import and test database connection
        from app.database.session import check_db_connection as db_check
        return await db_check()
    except ImportError:
        # Return healthy if no database configured
        return {
            "healthy": True,
            "message": "Database check skipped (using SQLite)",
            "type": "sqlite"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Database connection failed"
        }