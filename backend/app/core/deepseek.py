"""
DeepSeek API Client - Working Version with Custom HTTP Client
"""

import openai
import httpx
from typing import List, Dict, Any, AsyncGenerator
import asyncio
import json

from app.config import config
from app.utils.logger import logger


class DeepSeekClient:
    """Client for DeepSeek API"""
    
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.base_url = config.DEEPSEEK_BASE_URL
        self.model = config.DEEPSEEK_MODEL
        
        logger.info(f"Initializing DeepSeek client with base URL: {self.base_url}")
        
        # Create a custom HTTP client without any proxy settings
        # This avoids the 'proxies' argument conflict
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=self.http_client,
            max_retries=2
        )
    
    def count_tokens(self, text: str) -> int:
        """Simple token count approximation"""
        return len(text.split()) * 1.3
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost"""
        input_cost = (input_tokens / 1_000_000) * 0.14
        output_cost = (output_tokens / 1_000_000) * 0.28
        return input_cost + output_cost
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Get chat completion"""
        
        input_text = " ".join([m["content"] for m in messages])
        input_tokens = self.count_tokens(input_text)
        
        try:
            logger.info(f"Calling DeepSeek API with model: {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            output_tokens = self.count_tokens(content)
            cost = self.calculate_cost(input_tokens, output_tokens)
            
            logger.info(f"DeepSeek response received: {len(content)} chars, cost: ${cost:.6f}")
            
            return {
                "content": content,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                },
                "cost": cost,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion"""
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"DeepSeek stream error: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()


# Create global instance
deepseek_client = DeepSeekClient()