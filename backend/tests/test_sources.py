"""
Knowledge Sources Tests
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.knowledge_sources.wikipedia import WikipediaSource

@pytest.mark.asyncio
async def test_wikipedia_search():
    """Test Wikipedia search"""
    source = WikipediaSource()
    
    with patch.object(source.wiki, 'page') as mock_page:
        mock_page.return_value.exists.return_value = True
        mock_page.return_value.title = "Test"
        mock_page.return_value.summary = "Test summary"
        mock_page.return_value.fullurl = "https://en.wikipedia.org/wiki/Test"
        
        results = await source.search("Test")
        
        assert len(results) > 0
        assert results[0]["title"] == "Test"
        assert results[0]["source"] == "wikipedia"