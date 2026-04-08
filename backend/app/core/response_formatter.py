"""
Response Formatter Module
Format responses with proper structure and citations
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

class ResponseFormatter:
    """
    Format AI responses with proper structure
    """
    
    def format_response(
        self,
        content: str,
        sources: Optional[List[Dict]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Format complete response with sources
        """
        # Clean up content
        content = self._clean_content(content)
        
        # Extract citations if any
        citations = self._extract_citations(content)
        
        # Format response
        response = {
            "content": content,
            "formatted": self._add_formatting(content),
            "timestamp": datetime.utcnow().isoformat(),
            "word_count": len(content.split()),
            "character_count": len(content)
        }
        
        # Add sources if provided
        if sources and include_sources:
            response["sources"] = self._format_sources(sources)
            response["citations"] = citations
        
        return response
    
    def format_streaming_chunk(self, chunk: str) -> str:
        """
        Format streaming chunk
        """
        # Just pass through, client handles formatting
        return chunk
    
    def format_error(
        self,
        message: str,
        code: int = 500,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Format error response
        """
        return {
            "error": {
                "message": message,
                "code": code,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def format_search_results(
        self,
        results: List[Dict],
        query: str
    ) -> Dict[str, Any]:
        """
        Format search results
        """
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def format_conversation_history(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """
        Format conversation history
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("created_at", datetime.utcnow().isoformat())
            })
        return formatted
    
    def _clean_content(self, content: str) -> str:
        """
        Clean up response content
        """
        # Remove multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix spacing
        content = re.sub(r' +', ' ', content)
        
        # Ensure proper punctuation spacing
        content = re.sub(r'\.([A-Z])', r'. \1', content)
        
        return content.strip()
    
    def _add_formatting(self, content: str) -> str:
        """
        Add markdown formatting
        """
        # Already in markdown from AI, just ensure basic structure
        lines = content.split('\n')
        formatted = []
        
        for line in lines:
            # Ensure headers have space after #
            if line.startswith('#'):
                line = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', line)
            formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _extract_citations(self, content: str) -> List[Dict]:
        """
        Extract citations from content
        """
        citations = []
        
        # Look for [1], [2] style citations
        citation_pattern = r'\[(\d+)\]'
        matches = re.finditer(citation_pattern, content)
        
        for match in matches:
            citations.append({
                "number": match.group(1),
                "position": match.start()
            })
        
        return citations
    
    def _format_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Format source information
        """
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append({
                "id": i,
                "type": source.get("type", "unknown"),
                "title": source.get("title", "Unknown Source"),
                "relevance": source.get("relevance", 0.5),
                "url": source.get("url"),
                "snippet": source.get("content", "")[:200] + "..." if source.get("content") else None
            })
        return formatted
    
    def format_document_summary(
        self,
        document_id: str,
        filename: str,
        summary: str,
        key_points: List[str],
        stats: Dict
    ) -> Dict[str, Any]:
        """
        Format document summary
        """
        return {
            "document_id": document_id,
            "filename": filename,
            "summary": summary,
            "key_points": key_points,
            "statistics": {
                "pages": stats.get("pages", 0),
                "chunks": stats.get("chunks", 0),
                "tokens": stats.get("tokens", 0),
                "processing_time": stats.get("processing_time", 0)
            }
        }

# Global instance
response_formatter = ResponseFormatter()