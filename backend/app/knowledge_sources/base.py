"""
Base Knowledge Source
Abstract base class for all knowledge sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

class BaseKnowledgeSource(ABC):
    """
    Abstract base class for knowledge sources
    """
    
    def __init__(self, name: str, cache_ttl: int = 3600):
        self.name = name
        self.cache_ttl = cache_ttl
    
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge source
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get item by ID
        """
        pass
    
    def _format_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format result consistently
        """
        return {
            'id': self._generate_id(data),
            'source': self.name,
            'title': data.get('title', ''),
            'content': data.get('content', ''),
            'summary': data.get('summary', ''),
            'url': data.get('url', ''),
            'relevance': data.get('relevance', 0.5),
            'metadata': data.get('metadata', {}),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_id(self, data: Dict[str, Any]) -> str:
        """
        Generate unique ID for result
        """
        unique_str = f"{self.name}:{data.get('title', '')}:{data.get('url', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    def _clean_text(self, text: str, max_length: int = 1000) -> str:
        """
        Clean and truncate text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text