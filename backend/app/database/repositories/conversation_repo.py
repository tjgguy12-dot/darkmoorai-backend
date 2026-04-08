"""
Conversation Repository
Database operations for conversations and messages
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, desc

from app.database.repositories.base_repo import BaseRepository
from app.models.conversation import Conversation, Message
from app.database.session import async_session_maker

class ConversationRepository(BaseRepository):
    """
    Conversation repository with conversation-specific queries
    """
    
    def __init__(self):
        super().__init__(Conversation)
    
    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get conversations by user
        """
        return await self.get_many(user_id=user_id, skip=skip, limit=limit)
    
    async def get_with_messages(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation with all messages
        """
        async with async_session_maker() as session:
            # Get conversation
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return None
            
            # Get messages
            msg_stmt = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            
            msg_result = await session.execute(msg_stmt)
            messages = msg_result.scalars().all()
            
            conv_dict = conversation.to_dict()
            conv_dict["messages"] = [m.to_dict() for m in messages]
            
            return conv_dict
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        cost: float = 0.0,
        sources: List[Dict] = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Add message to conversation
        """
        message_repo = MessageRepository()
        
        message = await message_repo.create({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "tokens": tokens,
            "cost": cost,
            "sources": sources or [],
            "metadata": metadata or {}
        })
        
        # Update conversation message count
        await self.update(conversation_id, {
            "message_count": await message_repo.count(conversation_id=conversation_id),
            "total_tokens": await message_repo.sum_tokens(conversation_id=conversation_id),
            "total_cost": await message_repo.sum_cost(conversation_id=conversation_id)
        })
        
        return message
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation messages
        """
        message_repo = MessageRepository()
        return await message_repo.get_many(
            conversation_id=conversation_id,
            limit=limit
        )
    
    async def delete_by_user(self, user_id: str):
        """
        Delete all conversations for a user
        """
        conversations = await self.get_by_user(user_id)
        for conv in conversations:
            await self.delete(conv["id"])

class MessageRepository(BaseRepository):
    """
    Message repository with message-specific queries
    """
    
    def __init__(self):
        super().__init__(Message)
    
    async def get_by_conversation(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get messages by conversation
        """
        return await self.get_many(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit
        )
    
    async def count(self, **filters) -> int:
        """Count messages"""
        return await super().count(**filters)
    
    async def sum_tokens(self, conversation_id: str) -> int:
        """Sum tokens in conversation"""
        async with async_session_maker() as session:
            stmt = select(func.sum(Message.tokens)).where(
                Message.conversation_id == conversation_id
            )
            result = await session.execute(stmt)
            return result.scalar_one() or 0
    
    async def sum_cost(self, conversation_id: str) -> float:
        """Sum cost in conversation"""
        async with async_session_maker() as session:
            stmt = select(func.sum(Message.cost)).where(
                Message.conversation_id == conversation_id
            )
            result = await session.execute(stmt)
            return float(result.scalar_one() or 0.0)
    
    async def add_feedback(
        self,
        message_id: str,
        rating: int,
        feedback: Optional[str] = None
    ):
        """Add feedback to message"""
        await self.update(message_id, {
            "feedback_rating": rating,
            "feedback_text": feedback
        })