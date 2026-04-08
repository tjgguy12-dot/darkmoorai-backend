"""
Document Models
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Index, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.database import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    status = Column(String, default="pending")
    error = Column(String)
    progress = Column(Integer, default=0)
    
    pages = Column(Integer, default=0)
    chunks = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    extra_data = Column(JSON, default={})
    summary = Column(String)
    key_points = Column(JSON, default=[])
    
    ocr_used = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="documents")
    
    __table_args__ = (
        Index('idx_document_user_status', user_id, status),
        Index('idx_document_user_created', user_id, "created_at"),
    )


class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"
    
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    
    token_count = Column(Integer, default=0)
    extra_data = Column(JSON, default={})
    
    __table_args__ = (
        Index('idx_chunk_document', document_id),
        Index('idx_chunk_document_index', document_id, chunk_index),
    )