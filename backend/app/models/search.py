"""
Search History Model
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Index, DateTime
from datetime import datetime

from app.models.database import BaseModel


class SearchHistory(BaseModel):
    __tablename__ = "search_history"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    
    result_count = Column(Integer, default=0)
    sources_used = Column(JSON, default=[])
    
    selected_result = Column(JSON)
    
    was_helpful = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_search_user_created', user_id, created_at),
        Index('idx_search_query', query),
    )