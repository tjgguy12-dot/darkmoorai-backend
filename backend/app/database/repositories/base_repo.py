"""
Base Repository
Common CRUD operations for all models
"""

from typing import TypeVar, Type, Generic, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

from app.models.database import BaseModel
from app.database.session import async_session_maker

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get record by ID
        """
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            
            if instance:
                return instance.to_dict()
            return None
    
    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Get multiple records with filters
        """
        async with async_session_maker() as session:
            stmt = select(self.model)
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
            
            stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
            
            result = await session.execute(stmt)
            instances = result.scalars().all()
            
            return [i.to_dict() for i in instances]
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new record
        """
        async with async_session_maker() as session:
            instance = self.model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance.to_dict()
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update record
        """
        async with async_session_maker() as session:
            # Remove None values
            update_data = {k: v for k, v in data.items() if v is not None}
            
            if not update_data:
                return await self.get(id)
            
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
                .returning(self.model)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            instance = result.scalar_one_or_none()
            return instance.to_dict() if instance else None
    
    async def delete(self, id: str) -> bool:
        """
        Delete record
        """
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        """
        Count records with filters
        """
        async with async_session_maker() as session:
            stmt = select(func.count()).select_from(self.model)
            
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
            
            result = await session.execute(stmt)
            return result.scalar_one()
    
    async def exists(self, **filters) -> bool:
        """
        Check if record exists
        """
        count = await self.count(**filters)
        return count > 0