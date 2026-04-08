"""
Token Counter Module
Count tokens for cost estimation
"""

import tiktoken
from typing import Union, List

class TokenCounter:
    """
    Count tokens in text using OpenAI's tokenizer
    """
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize token counter
        """
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count(self, text: str) -> int:
        """
        Count tokens in text
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: List[dict]) -> int:
        """
        Count tokens in message list
        """
        total = 0
        for message in messages:
            total += self.count(message.get("content", ""))
            total += self.count(message.get("role", ""))
        return total
    
    def truncate(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to max tokens
        """
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated = self.encoding.decode(tokens[:max_tokens])
        return truncated
    
    def count_words(self, text: str) -> int:
        """
        Approximate word count
        """
        return len(text.split())
    
    def estimate_tokens_from_words(self, words: int) -> int:
        """
        Estimate tokens from word count (1 word ≈ 1.33 tokens)
        """
        return int(words * 1.33)
    
    def estimate_words_from_tokens(self, tokens: int) -> int:
        """
        Estimate words from token count
        """
        return int(tokens / 1.33)
    
    def get_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int = 0
    ) -> List[str]:
        """
        Split text into token-aware chunks
        """
        tokens = self.encoding.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            # Get chunk tokens
            end = min(i + chunk_size, len(tokens))
            chunk_tokens = tokens[i:end]
            
            # Decode chunk
            chunk = self.encoding.decode(chunk_tokens)
            chunks.append(chunk)
            
            # Move with overlap
            i += chunk_size - overlap
        
        return chunks
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        input_rate: float = 0.14,  # $ per million
        output_rate: float = 0.28   # $ per million
    ) -> float:
        """
        Calculate cost for tokens
        """
        input_cost = (input_tokens / 1_000_000) * input_rate
        output_cost = (output_tokens / 1_000_000) * output_rate
        return input_cost + output_cost

# Global instance
token_counter = TokenCounter()