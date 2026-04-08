"""
Document Repository
Database operations for documents and chunks
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, func

from app.database.repositories.base_repo import BaseRepository
from app.models.document import Document, DocumentChunk
from app.database.session import async_session_maker

class DocumentRepository(BaseRepository):
    """
    Document repository with document-specific queries
    """
    
    def __init__(self):
        super().__init__(Document)
    
    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get documents by user
        """
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status
        
        return await self.get_many(**filters, skip=skip, limit=limit)
    
    async def update_status(
        self,
        document_id: str,
        status: str,
        progress: int = None,
        error: str = None,
        pages: int = None,
        chunks: int = None
    ):
        """
        Update document processing status
        """
        updates = {"status": status}
        
        if progress is not None:
            updates["progress"] = progress
        if error is not None:
            updates["error"] = error
        if pages is not None:
            updates["pages"] = pages
        if chunks is not None:
            updates["chunks"] = chunks
        
        await self.update(document_id, updates)
    
    async def update_summary(self, document_id: str, summary: str, key_points: List[str]):
        """
        Update document summary
        """
        await self.update(document_id, {
            "summary": summary,
            "key_points": key_points
        })
    
    async def count_by_user(self, user_id: str) -> int:
        """
        Count documents by user
        """
        return await self.count(user_id=user_id)
    
    async def delete_by_user(self, user_id: str):
        """
        Delete all documents for a user
        """
        documents = await self.get_by_user(user_id)
        for doc in documents:
            await self.delete(doc["id"])

class DocumentChunkRepository(BaseRepository):
    """
    Document chunk repository
    """
    
    def __init__(self):
        super().__init__(DocumentChunk)
    
    async def get_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get chunks by document
        """
        return await self.get_many(document_id=document_id)
    
    async def delete_by_document(self, document_id: str):
        """
        Delete all chunks for a document
        """
        chunks = await self.get_by_document(document_id)
        for chunk in chunks:
            await self.delete(chunk["id"])
    
    async def count_by_document(self, document_id: str) -> int:
        """
        Count chunks in document
        """
        return await self.count(document_id=document_id)