"""
Text Chunker Module - Massive Document Support
Split 500MB documents into optimal chunks for RAG
"""

from typing import List, Dict, Any, Optional
import re
import math
from app.core.token_counter import token_counter
from app.utils.logger import logger

class TextChunker:
    """
    Split text into chunks for embedding and retrieval
    Supports massive documents (500MB+)
    """
    
    def __init__(
        self,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        respect_sentences: bool = True,
        respect_paragraphs: bool = True
    ):
        self.chunk_size = chunk_size  # 2000 words per chunk (massive!)
        self.chunk_overlap = chunk_overlap  # 200 word overlap
        self.respect_sentences = respect_sentences
        self.respect_paragraphs = respect_paragraphs
    
    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[Dict[str, Any]]:
        """
        Split massive document into chunks
        Supports 500MB+ documents with 2000 word chunks
        """
        # Use provided or default chunk size
        size = chunk_size or self.chunk_size
        ov = overlap or self.chunk_overlap
        
        logger.info(f"Chunking document: {len(text)} characters, {len(text.split())} words")
        
        # Clean text
        text = self._clean_text(text)
        
        # Try different splitting strategies based on document size
        word_count = len(text.split())
        
        if word_count < size:
            # Small document - return as single chunk
            chunks = [text]
        elif self.respect_paragraphs and "\n\n" in text:
            # Document with paragraphs - split by paragraphs
            chunks = self._split_by_paragraphs(text, size, ov)
        elif self.respect_sentences:
            # Split by sentences
            chunks = self._split_by_sentences(text, size, ov)
        else:
            # Simple word-based splitting
            chunks = self._split_by_words(text, size, ov)
        
        # Create chunk objects with metadata
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'metadata': metadata or {},
                'chunk_index': i,
                'word_count': len(chunk.split()),
                'token_count': token_counter.count(chunk),
                'char_count': len(chunk)
            }
            result.append(chunk_data)
        
        logger.info(f"Created {len(result)} chunks from massive document")
        logger.info(f"Average chunk size: {sum(c['word_count'] for c in result) / len(result):.0f} words")
        
        return result
    
    def _split_by_paragraphs(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text by paragraphs, respecting structure"""
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_words = len(para.split())
            
            if current_size + para_words <= chunk_size:
                # Add to current chunk
                current_chunk.append(para)
                current_size += para_words
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    # Get overlapping content from previous chunk
                    overlap_text = self._get_overlap_text(current_chunk, overlap)
                    current_chunk = [overlap_text, para] if overlap_text else [para]
                    current_size = len(overlap_text.split()) + para_words if overlap_text else para_words
                else:
                    current_chunk = [para]
                    current_size = para_words
        
        # Add last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_by_sentences(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text by sentences for better semantic chunks"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sent in sentences:
            sent_words = len(sent.split())
            
            if current_size + sent_words <= chunk_size:
                current_chunk.append(sent)
                current_size += sent_words
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    overlap_sentences = self._get_overlap_sentences(current_chunk, overlap)
                    current_chunk = overlap_sentences + [sent]
                    current_size = sum(len(s.split()) for s in current_chunk)
                else:
                    current_chunk = [sent]
                    current_size = sent_words
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_by_words(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple word-based splitting"""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            end = min(i + chunk_size, len(words))
            chunk = ' '.join(words[i:end])
            chunks.append(chunk)
            
            # Move with overlap
            i += chunk_size - overlap
        
        return chunks
    
    def _get_overlap_text(self, previous_chunk: List[str], overlap_words: int) -> str:
        """Get overlapping text from previous chunk"""
        full_text = ' '.join(previous_chunk)
        words = full_text.split()
        
        if len(words) <= overlap_words:
            return full_text
        
        overlap_text = ' '.join(words[-overlap_words:])
        return overlap_text
    
    def _get_overlap_sentences(self, previous_sentences: List[str], overlap_words: int) -> List[str]:
        """Get overlapping sentences based on word count"""
        overlap_sentences = []
        overlap_count = 0
        
        for sent in reversed(previous_sentences):
            sent_words = len(sent.split())
            if overlap_count + sent_words <= overlap_words:
                overlap_sentences.insert(0, sent)
                overlap_count += sent_words
            else:
                break
        
        return overlap_sentences
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix line breaks
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        
        return text.strip()
    
    def chunk_by_tokens(
        self,
        text: str,
        max_tokens: int = 20000,
        overlap_tokens: int = 2000
    ) -> List[str]:
        """
        Split text by token count (more accurate for large documents)
        """
        tokens = token_counter.encoding.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            end = min(i + max_tokens, len(tokens))
            chunk_tokens = tokens[i:end]
            
            # Decode chunk
            chunk = token_counter.encoding.decode(chunk_tokens)
            chunks.append(chunk)
            
            # Move with overlap
            i += max_tokens - overlap_tokens
        
        return chunks
    
    def chunk_with_structure(
        self,
        text: str,
        structure: Dict[str, Any],
        chunk_size: int = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk with document structure awareness (headings, sections)
        """
        size = chunk_size or self.chunk_size
        chunks = []
        
        if 'sections' in structure:
            # Handle structured documents
            for section in structure['sections']:
                section_chunks = self.chunk_document(
                    section['content'],
                    {'section': section['title'], 'level': section.get('level', 1)},
                    chunk_size=size
                )
                chunks.extend(section_chunks)
        else:
            # Regular chunking
            chunks = self.chunk_document(text, chunk_size=size)
        
        return chunks
    
    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {'count': 0}
        
        word_counts = [c['word_count'] for c in chunks]
        
        return {
            'count': len(chunks),
            'total_words': sum(word_counts),
            'avg_words': sum(word_counts) / len(chunks),
            'min_words': min(word_counts),
            'max_words': max(word_counts),
            'total_tokens': sum(c['token_count'] for c in chunks)
        }


# Global instance with massive settings
text_chunker = TextChunker(chunk_size=2000, chunk_overlap=200)