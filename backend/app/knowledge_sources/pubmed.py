"""
PubMed Knowledge Source
FREE! Access to 30M+ medical papers using requests
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

from app.knowledge_sources.base import BaseKnowledgeSource
from app.utils.logger import logger

class PubMedSource(BaseKnowledgeSource):
    """
    PubMed API integration using direct HTTP requests
    """
    
    def __init__(self):
        super().__init__(name="pubmed", cache_ttl=86400)  # 1 day cache
        self.session = None
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search PubMed articles
        """
        results = []
        session = await self._get_session()
        
        try:
            # First, search for IDs
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': limit,
                'retmode': 'json',
                'usehistory': 'y'
            }
            
            async with session.get(f"{self.base_url}esearch.fcgi", params=search_params) as response:
                if response.status == 200:
                    text = await response.text()
                    # Parse XML to get IDs
                    import re
                    ids = re.findall(r'<Id>(\d+)</Id>', text)
                    
                    if ids:
                        # Fetch details for these IDs
                        fetch_params = {
                            'db': 'pubmed',
                            'id': ','.join(ids),
                            'retmode': 'xml'
                        }
                        
                        async with session.get(f"{self.base_url}efetch.fcgi", params=fetch_params) as fetch_response:
                            if fetch_response.status == 200:
                                xml_text = await fetch_response.text()
                                results = self._parse_xml(xml_text)
            
            logger.info(f"PubMed search for '{query}' found {len(results)} articles")
            
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
        
        return results
    
    async def get_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get article by PMID
        """
        session = await self._get_session()
        
        try:
            params = {
                'db': 'pubmed',
                'id': identifier,
                'retmode': 'xml'
            }
            
            async with session.get(f"{self.base_url}efetch.fcgi", params=params) as response:
                if response.status == 200:
                    xml_text = await response.text()
                    results = self._parse_xml(xml_text)
                    if results:
                        return results[0]
        except Exception as e:
            logger.error(f"PubMed get_by_id error: {e}")
        
        return None
    
    def _parse_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response"""
        results = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall('.//PubmedArticle'):
                # Get title
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None else 'Unknown'
                
                # Get abstract
                abstract_elem = article.find('.//AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else 'No abstract available'
                
                # Get PMID
                pmid_elem = article.find('.//PMID')
                pmid = pmid_elem.text if pmid_elem is not None else None
                
                # Get authors
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.find('LastName')
                    fore_name = author.find('ForeName')
                    if last_name is not None:
                        name = last_name.text or ''
                        if fore_name is not None and fore_name.text:
                            name = f"{fore_name.text} {name}"
                        authors.append(name)
                
                # Get journal
                journal_elem = article.find('.//Title')
                journal = journal_elem.text if journal_elem is not None else None
                
                # Get publication date
                pub_date_elem = article.find('.//PubDate')
                pub_date = ''
                if pub_date_elem is not None:
                    year = pub_date_elem.find('Year')
                    month = pub_date_elem.find('Month')
                    if year is not None:
                        pub_date = year.text or ''
                        if month is not None and month.text:
                            pub_date += f"-{month.text}"
                
                result = self._format_result({
                    'title': title,
                    'summary': abstract[:500] if abstract else 'No abstract available',
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                    'relevance': 0.85,
                    'metadata': {
                        'pmid': pmid,
                        'authors': authors[:5],
                        'journal': journal,
                        'publication_date': pub_date
                    }
                })
                results.append(result)
                
        except Exception as e:
            logger.error(f"PubMed XML parsing error: {e}")
        
        return results
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()