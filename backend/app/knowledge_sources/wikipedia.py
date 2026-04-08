"""
Wikipedia Knowledge Source
FREE! Access to 55M+ Wikipedia articles using requests
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from app.knowledge_sources.base import BaseKnowledgeSource
from app.config import config
from app.utils.logger import logger

class WikipediaSource(BaseKnowledgeSource):
    """
    Wikipedia API integration using direct HTTP requests
    """
    
    def __init__(self):
        super().__init__(name="wikipedia", cache_ttl=604800)  # 7 days cache
        self.session = None
        self.base_url = "https://en.wikipedia.org/w/api.php"
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search Wikipedia
        """
        results = []
        session = await self._get_session()
        
        try:
            # Search Wikipedia
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': limit,
                'origin': '*'
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('query', {}).get('search', []):
                        # Get page details
                        page_params = {
                            'action': 'query',
                            'prop': 'extracts',
                            'exintro': True,
                            'explaintext': True,
                            'titles': item['title'],
                            'format': 'json',
                            'origin': '*'
                        }
                        
                        async with session.get(self.base_url, params=page_params) as page_response:
                            if page_response.status == 200:
                                page_data = await page_response.json()
                                pages = page_data.get('query', {}).get('pages', {})
                                
                                for page_id, page_info in pages.items():
                                    if page_id != '-1':
                                        results.append(self._format_result({
                                            'title': item['title'],
                                            'summary': page_info.get('extract', item.get('snippet', ''))[:500],
                                            'url': f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                                            'relevance': 0.9,
                                            'metadata': {
                                                'page_id': page_id,
                                                'word_count': page_info.get('wordcount', 0)
                                            }
                                        }))
            
            logger.info(f"Wikipedia search for '{query}' returned {len(results)} results")
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
        
        return results
    
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get Wikipedia page by title
        """
        session = await self._get_session()
        
        try:
            params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': identifier,
                'format': 'json',
                'origin': '*'
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get('query', {}).get('pages', {})
                    
                    for page_id, page_info in pages.items():
                        if page_id != '-1':
                            return self._format_result({
                                'title': identifier,
                                'summary': page_info.get('extract', '')[:1000],
                                'url': f"https://en.wikipedia.org/wiki/{identifier.replace(' ', '_')}",
                                'relevance': 1.0,
                                'metadata': {
                                    'page_id': page_id,
                                    'word_count': page_info.get('wordcount', 0)
                                }
                            })
        except Exception as e:
            logger.error(f"Wikipedia get_by_id error: {e}")
        
        return None
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()