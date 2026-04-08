"""
DarkmoorAI Advanced Multi-Search Service
Forces ALL 9 search engines to work
"""

import aiohttp
import asyncio
import random
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import quote_plus

# Suppress XML parsing warning
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class MultiSearchService:
    """
    Advanced search with multiple bypass techniques - ALL 9 ENGINES
    """
    
    def __init__(self):
        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        ]
        
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.8',
            'en-CA,en;q=0.7',
        ]
    
    def _get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate',  # Removed 'br' to avoid brotli issues
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    async def _fetch_with_retry(self, url: str, max_retries: int = 2) -> str:
        """Fetch URL with retry logic - simplified"""
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                timeout = aiohttp.ClientTimeout(total=15)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self._get_headers(), timeout=timeout, ssl=False) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:
                            await asyncio.sleep(3)
                            continue
            except Exception as e:
                print(f"Attempt {attempt + 1} error: {e}")
                continue
        return ""
    
    # ============================================================================
    # GOOGLE SEARCH
    # ============================================================================
    
    async def search_google(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Google"""
        results = []
        urls = [
            f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}",
        ]
        
        for url in urls:
            html = await self._fetch_with_retry(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for div in soup.find_all('div', class_='g')[:max_results]:
                    try:
                        title_elem = div.find('h3')
                        title = title_elem.get_text() if title_elem else ''
                        link_elem = div.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        desc_elem = div.find('div', class_='VwiC3b')
                        description = desc_elem.get_text() if desc_elem else ''
                        if title and url and 'google.com' not in url:
                            results.append({
                                'engine': 'Google',
                                'title': title,
                                'content': description[:500],
                                'url': url,
                                'relevance': 0.95
                            })
                    except:
                        continue
                if results:
                    break
        return results
    
    # ============================================================================
    # BING SEARCH
    # ============================================================================
    
    async def search_bing(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Bing"""
        results = []
        url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for li in soup.find_all('li', class_='b_algo')[:max_results]:
                try:
                    title_elem = li.find('h2')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = li.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = li.find('p')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Bing',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.92
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # DUCKDUCKGO SEARCH
    # ============================================================================
    
    async def search_duckduckgo(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search DuckDuckGo"""
        results = []
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for result in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = result.find('a', class_='result__url')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = result.find('a', class_='result__snippet')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'DuckDuckGo',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.88
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # YAHOO SEARCH
    # ============================================================================
    
    async def search_yahoo(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Yahoo"""
        results = []
        url = f"https://search.yahoo.com/search?p={quote_plus(query)}&n={max_results}"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for div in soup.find_all('div', class_='algo')[:max_results]:
                try:
                    title_elem = div.find('h3')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = div.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = div.find('p', class_='lh-16')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Yahoo',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.85
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # BRAVE SEARCH
    # ============================================================================
    
    async def search_brave(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Brave"""
        results = []
        url = f"https://search.brave.com/search?q={quote_plus(query)}&source=web"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for result in soup.find_all('div', class_='snippet')[:max_results]:
                try:
                    title_elem = result.find('h3')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = result.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = result.find('p')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Brave',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.87
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # QWANT SEARCH
    # ============================================================================
    
    async def search_qwant(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Qwant"""
        results = []
        url = f"https://www.qwant.com/?q={quote_plus(query)}&t=web"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for result in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_elem = result.find('a', class_='result-title')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = result.find('a', class_='result-title')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = result.find('p', class_='result-desc')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Qwant',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.86
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # MOJEEK SEARCH
    # ============================================================================
    
    async def search_mojeek(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Mojeek"""
        results = []
        url = f"https://www.mojeek.com/search?q={quote_plus(query)}&fmt=html"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for result in soup.find_all('li', class_='result')[:max_results]:
                try:
                    title_elem = result.find('a', class_='result-title')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = result.find('a', class_='result-title')
                    url = link_elem.get('href', '') if link_elem else ''
                    desc_elem = result.find('p', class_='result-desc')
                    description = desc_elem.get_text() if desc_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Mojeek',
                            'title': title,
                            'content': description[:500],
                            'url': url,
                            'relevance': 0.84
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # GOOGLE NEWS
    # ============================================================================
    
    async def search_google_news(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Google News"""
        results = []
        url = f"https://news.google.com/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for article in soup.find_all('article')[:max_results]:
                try:
                    title_elem = article.find('h3')
                    title = title_elem.get_text() if title_elem else ''
                    link_elem = article.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and url.startswith('./'):
                        url = 'https://news.google.com' + url[1:]
                    if title and url:
                        results.append({
                            'engine': 'Google News',
                            'title': title,
                            'content': title,
                            'url': url,
                            'relevance': 0.94
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # BING NEWS
    # ============================================================================
    
    async def search_bing_news(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Bing News"""
        results = []
        url = f"https://www.bing.com/news/search?q={quote_plus(query)}&count={max_results}"
        
        html = await self._fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for news in soup.find_all('div', class_='news-card')[:max_results]:
                try:
                    title_elem = news.find('a', class_='title')
                    title = title_elem.get_text() if title_elem else ''
                    url = title_elem.get('href', '') if title_elem else ''
                    source_elem = news.find('div', class_='source')
                    source = source_elem.get_text() if source_elem else ''
                    if title and url:
                        results.append({
                            'engine': 'Bing News',
                            'title': title,
                            'content': title,
                            'url': url,
                            'relevance': 0.93,
                            'metadata': {'source': source}
                        })
                except:
                    continue
        return results
    
    # ============================================================================
    # MASTER SEARCH - ALL 9 ENGINES
    # ============================================================================
    
    async def search_all(self, query: str, max_results_per_engine: int = 3) -> List[Dict]:
        """Search ALL 9 search engines in parallel"""
        
        print(f"🔍 Searching {query} across 9 engines...")
        
        # Run all searches in parallel
        results = await asyncio.gather(
            self.search_google(query, max_results_per_engine),
            self.search_bing(query, max_results_per_engine),
            self.search_duckduckgo(query, max_results_per_engine),
            self.search_yahoo(query, max_results_per_engine),
            self.search_brave(query, max_results_per_engine),
            self.search_qwant(query, max_results_per_engine),
            self.search_mojeek(query, max_results_per_engine),
            self.search_google_news(query, max_results_per_engine),
            self.search_bing_news(query, max_results_per_engine),
            return_exceptions=True
        )
        
        # Combine all results
        all_results = []
        engine_names = ['Google', 'Bing', 'DuckDuckGo', 'Yahoo', 'Brave', 'Qwant', 'Mojeek', 'Google News', 'Bing News']
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"⚠️ {engine_names[i]} search failed: {res}")
            elif isinstance(res, list):
                all_results.extend(res)
                print(f"✅ {engine_names[i]}: {len(res)} results")
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Sort by relevance
        unique_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        print(f"📊 TOTAL: {len(unique_results)} unique results from 9 engines")
        
        return unique_results


# Create global instance
search_service = MultiSearchService()