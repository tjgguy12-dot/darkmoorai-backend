"""
Knowledge Searcher - Enhanced with Google Search
"""

from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from app.services.google_search import google_search
from app.utils.logger import logger

class KnowledgeSearcher:
    """Search across multiple knowledge sources including Google"""
    
    def __init__(self):
        self.session = None
        self.google = google_search
    
    async def search_all(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        max_results: int = 5,
        include_google: bool = True
    ) -> List[Dict[str, Any]]:
        """Search across all enabled sources including Google"""
        
        results = []
        tasks = []
        
        # Source handlers
        sources = {
            "wikipedia": self.search_wikipedia,
            "arxiv": self.search_arxiv,
            "pubmed": self.search_pubmed,
            "openlibrary": self.search_openlibrary,
            "google": self.search_google,
            "google_news": self.search_google_news
        }
        
        # Determine which sources to search
        if source_types:
            sources_to_search = [s for s in source_types if s in sources]
        else:
            sources_to_search = ["wikipedia", "google", "google_news"]  # Default sources
        
        # Always include Google if requested
        if include_google and "google" not in sources_to_search:
            sources_to_search.append("google")
        
        # Create search tasks
        for source in sources_to_search:
            if source == "google":
                tasks.append(self.search_google(query, max_results))
            elif source == "google_news":
                tasks.append(self.search_google_news(query, max_results))
            elif source in sources:
                tasks.append(sources[source](query, max_results))
        
        # Run searches in parallel
        if tasks:
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"Search error for {sources_to_search[i]}: {result}")
                else:
                    results.extend(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return results[:max_results * len(sources_to_search)]
    
    async def search_google(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Google for current information"""
        try:
            results = await self.google.search(query, max_results)
            
            # Format results
            formatted = []
            for r in results:
                formatted.append({
                    'source': 'google',
                    'title': r.get('title', ''),
                    'content': r.get('description', ''),
                    'url': r.get('url', ''),
                    'relevance': 0.85,
                    'metadata': {
                        'domain': r.get('domain', ''),
                        'type': 'web'
                    }
                })
            
            logger.info(f"Google search for '{query}' returned {len(formatted)} results")
            return formatted
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    async def search_google_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Google News for current news"""
        try:
            results = await self.google.search_news(query, max_results)
            
            formatted = []
            for r in results:
                formatted.append({
                    'source': 'google_news',
                    'title': r.get('title', ''),
                    'content': r.get('description', ''),
                    'url': r.get('url', ''),
                    'relevance': 0.9,
                    'metadata': {
                        'source': r.get('source', ''),
                        'time': r.get('time', ''),
                        'type': 'news'
                    }
                })
            
            logger.info(f"Google News search for '{query}' returned {len(formatted)} results")
            return formatted
            
        except Exception as e:
            logger.error(f"Google News search error: {e}")
            return []
    
    async def get_page_content(self, url: str) -> str:
        """Get full content of a web page"""
        return await self.google.get_page_content(url)
    
    # Other search methods (wikipedia, arxiv, etc.) remain the same...
    
    async def search_wikipedia(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia"""
        # ... existing code ...
        pass
    
    async def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search arXiv"""
        # ... existing code ...
        pass
    
    async def search_pubmed(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search PubMed"""
        # ... existing code ...
        pass
    
    async def search_openlibrary(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Open Library"""
        # ... existing code ...
        pass