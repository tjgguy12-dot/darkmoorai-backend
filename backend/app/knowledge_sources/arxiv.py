"""
arXiv Knowledge Source
FREE! Access to 2M+ scientific papers using requests
"""

import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

from app.knowledge_sources.base import BaseKnowledgeSource
from app.utils.logger import logger

class ArxivSource(BaseKnowledgeSource):
    """
    arXiv API integration using direct HTTP requests
    """
    
    def __init__(self):
        super().__init__(name="arxiv", cache_ttl=86400)  # 1 day cache
        self.session = None
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search arXiv papers
        """
        results = []
        session = await self._get_session()
        
        try:
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': limit,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    results = self._parse_xml(text)
            
            logger.info(f"arXiv search for '{query}' found {len(results)} papers")
            
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
        
        return results
    
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get paper by arXiv ID
        """
        session = await self._get_session()
        
        try:
            params = {
                'id_list': identifier,
                'max_results': 1
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    results = self._parse_xml(text)
                    if results:
                        return results[0]
        except Exception as e:
            logger.error(f"arXiv get_by_id error: {e}")
        
        return None
    
    def _parse_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        results = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # Define namespaces
            namespaces = {
                'arxiv': 'http://arxiv.org/schemas/atom',
                'default': 'http://www.w3.org/2005/Atom'
            }
            
            for entry in root.findall('.//default:entry', namespaces):
                title_elem = entry.find('default:title', namespaces)
                summary_elem = entry.find('default:summary', namespaces)
                id_elem = entry.find('default:id', namespaces)
                
                # Get authors
                authors = []
                for author in entry.findall('default:author', namespaces):
                    name_elem = author.find('default:name', namespaces)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text)
                
                # Get categories
                categories = []
                for cat in entry.findall('default:category', namespaces):
                    term = cat.get('term')
                    if term:
                        categories.append(term)
                
                # Get published date
                published_elem = entry.find('default:published', namespaces)
                published = published_elem.text if published_elem is not None else None
                
                # Get PDF link
                pdf_url = None
                for link in entry.findall('default:link', namespaces):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href')
                        break
                
                result = self._format_result({
                    'title': title_elem.text if title_elem is not None else 'Unknown',
                    'summary': summary_elem.text[:500] if summary_elem is not None else 'No summary available',
                    'url': id_elem.text if id_elem is not None else None,
                    'pdf_url': pdf_url,
                    'relevance': 0.9,
                    'metadata': {
                        'authors': authors,
                        'published': published,
                        'categories': categories
                    }
                })
                results.append(result)
                
        except Exception as e:
            logger.error(f"arXiv XML parsing error: {e}")
        
        return results
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()