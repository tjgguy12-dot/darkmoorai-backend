"""
RAG Engine Tests
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.rag_engine import RAGEngine

@pytest.mark.asyncio
async def test_rag_answer_question():
    """Test RAG answer generation"""
    engine = RAGEngine()
    
    with patch.object(engine.deepseek, 'chat_completion', new_callable=AsyncMock) as mock_deepseek:
        mock_deepseek.return_value = {
            "content": "This is a test answer",
            "tokens": {"input": 100, "output": 50, "total": 150},
            "cost": 0.0001
        }
        
        response = await engine.answer_question(
            question="What is AI?",
            user_id="test_user",
            use_web_search=False
        )
        
        assert "answer" in response
        assert "sources" in response
        assert "cost" in response