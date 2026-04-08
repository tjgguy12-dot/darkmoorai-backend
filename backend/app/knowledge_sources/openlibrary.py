"""
Open Library Knowledge Source
FREE! Access to 20M+ books
"""

import aiohttp
from typing import List, Dict, Any, Optional

from app.knowledge_sources.base import BaseKnowledgeSource
from app.utils.logger import logger

class OpenLibrarySource(BaseKnowledgeSource):
    """
    Open Library API integration for books
    """
    
    def __init__(self):
        super().__init__(name="openlibrary", cache_ttl=604800)  # 7 days cache
        self.base_url = "https://openlibrary.org"
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
                'q': query,
                'limit': limit,
                'fields': 'key,title,author_name,first_publish_year,subject,isbn,cover_i,description'
            }
            
            async with session.get(
                f"{self.base_url}/search.json",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for doc in data.get('docs', []):
                        results.append(self._doc_to_dict(doc))
            
            logger.info(f"Open Library search for '{query}' found {len(results)} books")
            
        except Exception as e:
            logger.error(f"Open Library search error: {e}")
        
        return results
    
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get book by Open Library ID (OLID) or ISBN
        """
        session = await self._get_session()
        
        try:
            if identifier.startswith('OL'):
                # Get by OLID
                async with session.get(f"{self.base_url}/books/{identifier}.json") as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._work_to_dict(data, identifier)
            else:
                # Assume ISBN
                async with session.get(f"{self.base_url}/isbn/{identifier}.json") as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._work_to_dict(data, identifier)
        except Exception as e:
            logger.error(f"Open Library get_by_id error: {e}")
        
        return None
    
    async def get_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Get book by ISBN
        """
        return await self.get_by_id(isbn)
    
    async def get_by_olid(self, olid: str) -> Optional[Dict[str, Any]]:
        """
        Get book by Open Library ID
        """
        return await self.get_by_id(olid)
    
    async def search_by_subject(
        self,
        subject: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search books by subject
        """
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.base_url}/subjects/{subject}.json",
                params={'limit': limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    works = data.get('works', [])
                    return [self._work_to_dict(w) for w in works]
        except Exception as e:
            logger.error(f"Open Library subject search error: {e}")
        
        return []
    
    async def get_author(self, author_id: str) -> Optional[Dict[str, Any]]:
        """
        Get author information
        """
        session = await self._get_session()
        
        try:
            async with session.get(f"{self.base_url}/authors/{author_id}.json") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': data.get('name'),
                        'birth_date': data.get('birth_date'),
                        'death_date': data.get('death_date'),
                        'bio': data.get('bio', ''),
                        'wikipedia': data.get('wikipedia'),
                        'photos': data.get('photos', [])
                    }
        except Exception as e:
            logger.error(f"Open Library author error: {e}")
        
        return None
    
    def _doc_to_dict(self, doc: Dict) -> Dict[str, Any]:
        """Convert search document to result"""
        cover_id = doc.get('cover_i')
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
        
        return self._format_result({
            'title': doc.get('title', 'Unknown'),
            'summary': self._clean_text(doc.get('description', 'No description available'), 500),
            'content': self._clean_text(doc.get('description', 'No description available'), 1000),
            'url': f"{self.base_url}{doc.get('key', '')}" if doc.get('key') else None,
            'relevance': 0.8,
            'metadata': {
                'authors': doc.get('author_name', ['Unknown']),
                'year': doc.get('first_publish_year'),
                'subjects': doc.get('subject', [])[:5],
                'isbn': doc.get('isbn', [])[:3] if doc.get('isbn') else [],
                'cover_url': cover_url,
                'pages': doc.get('number_of_pages_median')
            }
        })
    
    def _work_to_dict(self, work: Dict, identifier: str = None) -> Dict[str, Any]:
        """Convert work to result"""
        covers = work.get('covers', [])
        cover_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-M.jpg" if covers else None
        
        return self._format_result({
            'title': work.get('title', 'Unknown'),
            'summary': self._clean_text(work.get('description', 'No description available'), 500),
            'content': self._clean_text(work.get('description', 'No description available'), 1000),
            'url': f"{self.base_url}{work.get('key', '')}",
            'relevance': 0.9,
            'metadata': {
                'authors': work.get('authors', []),
                'subjects': work.get('subjects', [])[:5],
                'cover_url': cover_url,
                'pages': work.get('number_of_pages'),
                'publish_date': work.get('publish_date'),
                'publishers': work.get('publishers', [])
            }
        })
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()