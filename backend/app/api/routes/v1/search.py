"""
Search Routes - Complete with Google, Wikipedia, arXiv, PubMed
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import random
import time

router = APIRouter()


class SearchResult(BaseModel):
    source: str
    title: str
    summary: str
    url: str
    relevance: float
    content: Optional[str] = None


# User agents for Google scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


# ============================================================================
# GOOGLE SEARCH (FREE - No API Key)
# ============================================================================

@router.get("/google")
async def search_google(
    q: str = Query(..., min_length=2),
    max_results: int = Query(5, ge=1, le=10)
):
    """Search Google - FREE web scraping"""
    results = []
    
    try:
        search_url = f"https://www.google.com/search?q={q.replace(' ', '+')}&num={max_results}"
        
        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(random.uniform(1, 2))
            async with session.get(search_url, headers=get_headers()) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for div in soup.find_all('div', class_='g')[:max_results]:
                        try:
                            title_elem = div.find('h3')
                            title = title_elem.get_text() if title_elem else ''
                            
                            link_elem = div.find('a')
                            url = link_elem.get('href', '')
                            if url.startswith('/url?q='):
                                url = url.split('/url?q=')[1].split('&')[0]
                            
                            desc_elem = div.find('div', class_='VwiC3b')
                            description = desc_elem.get_text() if desc_elem else ''
                            
                            if title and url:
                                results.append({
                                    'source': 'google',
                                    'title': title,
                                    'summary': description[:300],
                                    'url': url,
                                    'relevance': 0.9,
                                    'content': description
                                })
                        except Exception:
                            continue
    except Exception as e:
        print(f"Google search error: {e}")
    
    return results


@router.get("/google_news")
async def search_google_news(
    q: str = Query(..., min_length=2),
    max_results: int = Query(5, ge=1, le=10)
):
    """Search Google News - FREE web scraping"""
    results = []
    
    try:
        search_url = f"https://www.google.com/search?q={q.replace(' ', '+')}&tbm=nws&num={max_results}"
        
        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(random.uniform(1, 2))
            async with session.get(search_url, headers=get_headers()) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for article in soup.find_all('div', class_='SoaBEf')[:max_results]:
                        try:
                            title_elem = article.find('h3')
                            title = title_elem.get_text() if title_elem else ''
                            
                            link_elem = article.find('a')
                            url = link_elem.get('href', '') if link_elem else ''
                            
                            source_elem = article.find('div', class_='XTjFC')
                            source = source_elem.get_text() if source_elem else ''
                            
                            time_elem = article.find('span', class_='r0bn4c')
                            time_ago = time_elem.get_text() if time_elem else ''
                            
                            desc_elem = article.find('div', class_='GI74Re')
                            description = desc_elem.get_text() if desc_elem else ''
                            
                            results.append({
                                'source': 'google_news',
                                'title': title,
                                'summary': description[:300],
                                'url': url,
                                'relevance': 0.9,
                                'metadata': {
                                    'source': source,
                                    'time': time_ago
                                },
                                'content': description
                            })
                        except Exception:
                            continue
    except Exception as e:
        print(f"Google News error: {e}")
    
    return results


# ============================================================================
# WIKIPEDIA SEARCH
# ============================================================================

@router.get("/wikipedia")
async def search_wikipedia(
    q: str = Query(..., min_length=2),
    max_results: int = Query(5, ge=1, le=10)
):
    """Search Wikipedia"""
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': q,
                'format': 'json',
                'srlimit': max_results,
                'origin': '*'
            }
            
            async with session.get('https://en.wikipedia.org/w/api.php', params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('query', {}).get('search', []):
                        results.append({
                            'source': 'wikipedia',
                            'title': item['title'],
                            'summary': item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
                            'url': f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                            'relevance': 0.85,
                            'content': item.get('snippet', '')
                        })
    except Exception as e:
        print(f"Wikipedia error: {e}")
    
    return results


# ============================================================================
# ARXIV SEARCH (Scientific Papers)
# ============================================================================

@router.get("/arxiv")
async def search_arxiv(
    q: str = Query(..., min_length=2),
    max_results: int = Query(5, ge=1, le=10)
):
    """Search arXiv scientific papers"""
    results = []
    
    try:
        params = {
            'search_query': f'all:{q}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('http://export.arxiv.org/api/query', params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    root = ET.fromstring(text)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    for entry in root.findall('.//atom:entry', ns):
                        title_elem = entry.find('atom:title', ns)
                        summary_elem = entry.find('atom:summary', ns)
                        id_elem = entry.find('atom:id', ns)
                        
                        authors = []
                        for author in entry.findall('.//atom:author', ns):
                            name = author.find('atom:name', ns)
                            if name is not None:
                                authors.append(name.text)
                        
                        results.append({
                            'source': 'arxiv',
                            'title': title_elem.text if title_elem is not None else 'Unknown',
                            'summary': (summary_elem.text[:300] if summary_elem is not None else 'No summary'),
                            'url': id_elem.text if id_elem is not None else '',
                            'relevance': 0.85,
                            'metadata': {'authors': authors[:3]},
                            'content': summary_elem.text[:500] if summary_elem else ''
                        })
    except Exception as e:
        print(f"arXiv error: {e}")
    
    return results


# ============================================================================
# PUBMED SEARCH (Medical Research)
# ============================================================================

@router.get("/pubmed")
async def search_pubmed(
    q: str = Query(..., min_length=2),
    max_results: int = Query(5, ge=1, le=10)
):
    """Search PubMed medical papers"""
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            search_params = {
                'db': 'pubmed',
                'term': q,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            async with session.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=search_params) as search_resp:
                if search_resp.status == 200:
                    text = await search_resp.text()
                    ids = re.findall(r'<Id>(\d+)</Id>', text)
                    
                    if ids:
                        fetch_params = {
                            'db': 'pubmed',
                            'id': ','.join(ids),
                            'retmode': 'xml'
                        }
                        
                        async with session.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', params=fetch_params) as fetch_resp:
                            if fetch_resp.status == 200:
                                xml_text = await fetch_resp.text()
                                root = ET.fromstring(xml_text)
                                
                                for article in root.findall('.//PubmedArticle'):
                                    title_elem = article.find('.//ArticleTitle')
                                    abstract_elem = article.find('.//AbstractText')
                                    pmid_elem = article.find('.//PMID')
                                    
                                    results.append({
                                        'source': 'pubmed',
                                        'title': title_elem.text if title_elem is not None else 'Unknown',
                                        'summary': (abstract_elem.text[:300] if abstract_elem is not None else 'No abstract'),
                                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid_elem.text}/" if pmid_elem is not None else '',
                                        'relevance': 0.85,
                                        'content': abstract_elem.text[:500] if abstract_elem else ''
                                    })
    except Exception as e:
        print(f"PubMed error: {e}")
    
    return results


# ============================================================================
# RESEARCH MODE - SEARCH ALL SOURCES
# ============================================================================

@router.get("/research")
async def research_mode(
    q: str = Query(..., min_length=2),
    max_results: int = Query(3, ge=1, le=5)
):
    """Search ALL sources for research mode"""
    
    # Run all searches in parallel
    results = await asyncio.gather(
        search_google(q, max_results),
        search_google_news(q, max_results),
        search_wikipedia(q, max_results),
        search_arxiv(q, max_results),
        search_pubmed(q, max_results),
        return_exceptions=True
    )
    
    # Combine all results
    all_results = []
    source_names = ['google', 'google_news', 'wikipedia', 'arxiv', 'pubmed']
    
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"Error in {source_names[i]}: {res}")
        else:
            all_results.extend(res)
    
    # Sort by relevance
    all_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    
    return {
        'query': q,
        'total': len(all_results),
        'results': all_results[:max_results * 5]  # Return up to 15 results
    }