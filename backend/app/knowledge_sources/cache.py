"""
Knowledge Cache Module
Cache for knowledge source results
"""

import json
import hashlib
from typing import Optional, Any
from datetime import datetime, timedelta

from app.core.cache import cache
from app.utils.logger import logger

class KnowledgeCache:
    """
    Specialized cache for knowledge sources
    """
    
    def __init__(self):
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached result"""
        return await cache.get(f"knowledge:{key}")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Cache result"""
        await cache.set(
            f"knowledge:{key}",
            value,
            ttl=ttl or self.default_ttl
        )
    
    async def clear_source(self, source_name: str):
        """Clear cache for specific source"""
        pattern = f"knowledge:search:{source_name}:*"
        await cache.clear_pattern(pattern)
        logger.info(f"Cleared cache for source: {source_name}")
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'status': 'active',
            'default_ttl': self.default_ttl
        }