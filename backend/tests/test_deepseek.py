"""
DeepSeek Client Tests
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.deepseek import DeepSeekClient

@pytest.mark.asyncio
async def test_deepseek_chat_completion():
    """Test chat completion"""
    client = DeepSeekClient()
    
    with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[AsyncMock(
                message=AsyncMock(content="Test response"),
                finish_reason="stop"
            )]
        )
        
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert response["content"] == "Test response"
        assert "tokens" in response
        assert "cost" in response

@pytest.mark.asyncio
async def test_deepseek_cost_calculation():
    """Test cost calculation"""
    client = DeepSeekClient()
    
    cost = client.calculate_cost(input_tokens=1000, output_tokens=500)
    
    # 1000 input tokens at $0.14/M = $0.00014
    # 500 output tokens at $0.28/M = $0.00014
    # Total = $0.00028
    assert cost == pytest.approx(0.00028, rel=0.001)