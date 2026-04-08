"""
RAG Engine - Simplified Working Version
"""

from typing import List, Dict, Any, Optional
import uuid
import asyncio
from datetime import datetime

from app.core.deepseek import deepseek_client
from app.knowledge_sources.searcher import KnowledgeSearcher
from app.utils.logger import logger


class RAGEngine:
    """Retrieval-Augmented Generation engine"""
    
    def __init__(self):
        self.searcher = KnowledgeSearcher()
    
    async def answer_with_sources(
        self,
        question: str,
        user_id: str,
        use_web_search: bool = True,
        use_documents: bool = False,
        research_mode: bool = False,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Answer question using RAG"""
        
        start_time = datetime.utcnow()
        contexts = []
        sources = []
        
        # Web search if enabled
        if use_web_search:
            try:
                web_results = await self.searcher.search_all(question, None, 3)
                
                for result in web_results:
                    contexts.append({
                        'content': result.get('content', result.get('summary', '')),
                        'source': result['source'],
                        'title': result['title'],
                        'url': result.get('url'),
                        'relevance': result.get('relevance', 0.8)
                    })
            except Exception as e:
                logger.error(f"Search error: {e}")
        
        # Build context text
        context_text = self._build_context_text(contexts)
        
        # Build sources list
        for ctx in contexts:
            sources.append({
                'type': ctx['source'],
                'title': ctx['title'],
                'url': ctx.get('url'),
                'relevance': ctx['relevance']
            })
        
        # Build prompt
        prompt = self._build_prompt(question, context_text, research_mode)
        
        # Get answer from DeepSeek
        try:
            response = await deepseek_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'answer': response['content'],
                'sources': sources,
                'cost': response['cost'],
                'tokens_used': response['tokens']['total'],
                'processing_time': processing_time,
                'contexts_used': len(contexts)
            }
            
        except Exception as e:
            logger.error(f"RAG answer error: {e}")
            raise
    
    def _build_context_text(self, contexts: List[Dict]) -> str:
        """Build formatted context text"""
        if not contexts:
            return ""
        
        context_parts = []
        for i, ctx in enumerate(contexts, 1):
            source_emoji = {
                'wikipedia': '📖',
                'arxiv': '🔬',
                'pubmed': '🏥',
                'openlibrary': '📚',
                'document': '📄'
            }.get(ctx['source'], '📌')
            
            context_parts.append(f"[{source_emoji} Source {i}: {ctx['title']}]\n{ctx['content'][:500]}\n")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context_text: str, research_mode: bool) -> str:
        """Build prompt"""
        
        if research_mode:
            instruction = """You are DarkmoorAI in RESEARCH MODE. Provide detailed, well-researched answers with citations."""
        else:
            instruction = """You are DarkmoorAI, a helpful AI assistant. Provide clear, concise answers."""
        
        if context_text:
            prompt = f"""{instruction}

Here are the sources you can use:

{context_text}

Question: {question}

Please answer based on the sources above. Cite your sources using [Source 1], etc."""

        else:
            prompt = f"""{instruction}

Question: {question}

Please answer based on your knowledge."""
        
        return prompt
    
    async def answer_with_document(
        self,
        question: str,
        document_content: str,
        document_name: str
    ) -> Dict[str, Any]:
        """Answer based on document"""
        
        prompt = f"""You are DarkmoorAI. Analyze this document:

Document: {document_name}
Content: {document_content[:2000]}

Question: {question}

Answer based on the document:"""

        try:
            response = await deepseek_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'answer': response['content'],
                'cost': response['cost'],
                'tokens_used': response['tokens']['total']
            }
            
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            raise


# Create global instance
rag_engine = RAGEngine()