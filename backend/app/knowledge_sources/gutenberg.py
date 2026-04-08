"""
Project Gutenberg Knowledge Source
FREE! Access to 70K+ classic books
"""

import aiohttp
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

from app.knowledge_sources.base import BaseKnowledgeSource
from app.utils.logger import logger

class GutenbergSource(BaseKnowledgeSource):
    """
    Project Gutenberg API integration for classic books
    """
    
    def __init__(self):
        super().__init__(name="gutenberg", cache_ttl=604800)  # 7 days cache
        self.base_url = "https://www.gutenberg.org"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for books
        """
        results = []
        session = await self._get_session()
        
        try:
            params = {
                'search': query,
                'limit': limit,
                'format': 'json'
            }
            
            async with session.get(
                f"{self.base_url}/ebooks/search/",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for book in data.get('results', [])[:limit]:
                        results.append(await self._book_to_dict(book))
            
            logger.info(f"Gutenberg search for '{query}' found {len(results)} books")
            
        except Exception as e:
            logger.error(f"Gutenberg search error: {e}")
        
        return results
    
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get book by Gutenberg ID
        """
        session = await self._getSession()
        
        try:
            # Try to parse as integer
            book_id = int(identifier)
            
            async with session.get(f"{self.base_url}/ebooks/{book_id}.json") as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._book_to_dict(data)
        except:
            pass
        
        return None
    
    async def _book_to_dict(self, book_data: Dict) -> Dict[str, Any]:
        """Convert book data to result"""
        book_id = book_data.get('id')
        
        # Get text content (first available format)
        formats = book_data.get('formats', {})
        text_url = None
        
        # Prefer plain text
        for fmt, url in formats.items():
            if 'text/plain' in fmt:
                text_url = url
                break
        
        # Get first few paragraphs if available
        content = ""
        if text_url:
            content = await self._fetch_text_preview(text_url)
        
        return self._format_result({
            'title': book_data.get('title', 'Unknown'),
            'summary': self._clean_text(book_data.get('description', ''), 500),
            'content': self._clean_text(content, 1000),
            'url': f"{self.base_url}/ebooks/{book_id}",
            'relevance': 0.8,
            'metadata': {
                'authors': book_data.get('authors', []),
                'subjects': book_data.get('subjects', [])[:5],
                'bookshelves': book_data.get('bookshelves', []),
                'language': book_data.get('language', 'en'),
                'downloads': book_data.get('download_count'),
                'formats': list(book_data.get('formats', {}).keys())
            }
        })
    
    async def _fetch_text_preview(self, url: str, max_chars: int = 2000) -> str:
        """Fetch text preview from URL"""
        session = await self._get_session()
        
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    # Clean and truncate
                    text = ' '.join(text.split())[:max_chars]
                    return text
        except:
            pass
        
        return ""
    
    async def get_by_author(
        self,
        author: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get books by author
        """
        return await self.search(f"author:{author}", limit)
    
    async def get_by_subject(
        self,
        subject: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get books by subject
        """
        return await self.search(f"subject:{subject}", limit)
    
    async def get_popular(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular books
        """
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.base_url}/ebooks/search/",
                params={'sort': 'downloads', 'limit': limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    books = data.get('results', [])
                    return [await self._book_to_dict(b) for b in books]
        except Exception as e:
            logger.error(f"Gutenberg popular error: {e}")
        
        return []
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()