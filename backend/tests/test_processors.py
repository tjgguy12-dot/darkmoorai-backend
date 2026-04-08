"""
Document Processor Tests
"""

import pytest
from app.document_processor.chunker import TextChunker

def test_text_chunker():
    """Test text chunking"""
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    
    text = "This is a test sentence. " * 20
    chunks = chunker.chunk_document(text)
    
    assert len(chunks) > 0
    assert all(c["word_count"] <= 110 for c in chunks)

def test_text_cleaner():
    """Test text cleaning"""
    from app.document_processor.text_cleaner import TextCleaner
    
    cleaner = TextCleaner()
    
    text = "This  is   a test.   Multiple spaces."
    cleaned = cleaner.clean(text)
    
    assert "  " not in cleaned