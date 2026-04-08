"""
Google Search Service - Free Web Scraping
No API key required - scrapes Google search results directly
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
import random
import time

class GoogleSearch:
    """
    Free Google Search using web scraping
    No API key needed - works like a real browser
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
    
    def _get_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Google and return results
        """
        results = []
        
        # Format query for Google
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}"
        
        async with aiohttp.ClientSession() as session:
            try:
                # Add delay to avoid rate limiting
                await asyncio.sleep(random.uniform(1, 2))
                
                async with session.get(search_url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        html = await response.text()
                        results = self._parse_google_results(html, num_results)
                    else:
                        print(f"Google search failed with status: {response.status}")
                        
            except Exception as e:
                print(f"Google search error: {e}")
                
        return results
    
    def _parse_google_results(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Parse Google search results from HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all search result divs
        search_divs = soup.find_all('div', class_='g')
        
        for div in search_divs[:num_results]:
            try:
                # Extract title
                title_elem = div.find('h3')
                if not title_elem:
                    continue
                title = title_elem.get_text()
                
                # Extract URL
                link_elem = div.find('a')
                url = link_elem.get('href') if link_elem else ''
                if url.startswith('/url?q='):
                    url = url.split('/url?q=')[1].split('&')[0]
                
                # Extract description/snippet
                desc_elem = div.find('div', class_='VwiC3b')
                if not desc_elem:
                    desc_elem = div.find('span', class_='aCOpRe')
                description = desc_elem.get_text() if desc_elem else ''
                
                # Extract source/domain
                domain = ''
                cite_elem = div.find('cite')
                if cite_elem:
                    domain = cite_elem.get_text()
                
                results.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'domain': domain,
                    'source': 'google'
                })
                
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue
        
        return results
    
    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Google News
        """
        results = []
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws&num={num_results}"
        
        async with aiohttp.ClientSession() as session:
            try:
                await asyncio.sleep(random.uniform(1, 2))
                async with session.get(search_url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        html = await response.text()
                        results = self._parse_google_news_results(html, num_results)
            except Exception as e:
                print(f"Google News search error: {e}")
                
        return results
    
    def _parse_google_news_results(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Parse Google News results
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find news articles
        articles = soup.find_all('div', class_='SoaBEf')
        
        for article in articles[:num_results]:
            try:
                title_elem = article.find('h3')
                title = title_elem.get_text() if title_elem else ''
                
                link_elem = article.find('a')
                url = link_elem.get('href') if link_elem else ''
                
                source_elem = article.find('div', class_='XTjFC')
                source = source_elem.get_text() if source_elem else ''
                
                time_elem = article.find('span', class_='r0bn4c')
                time_ago = time_elem.get_text() if time_elem else ''
                
                description_elem = article.find('div', class_='GI74Re')
                description = description_elem.get_text() if description_elem else ''
                
                results.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'time': time_ago,
                    'description': description,
                    'type': 'news'
                })
                
            except Exception as e:
                print(f"Error parsing news: {e}")
                continue
        
        return results
    
    async def get_page_content(self, url: str) -> str:
        """
        Get full content of a web page
        """
        async with aiohttp.ClientSession() as session:
            try:
                await asyncio.sleep(random.uniform(0.5, 1))
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Limit to first 5000 characters
                        return text[:5000]
            except Exception as e:
                print(f"Error fetching page content: {e}")
                
        return ""


# Global instance
google_search = GoogleSearch()