"""
Admin Routes
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

router = APIRouter()


@router.get("/users")
async def get_users():
    """Get all users"""
    return {"users": [], "total": 0}


@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_users": 0,
        "active_users": 0,
        "total_messages": 0,
        "total_documents": 0,
        "system_health": "healthy"
    }


@router.get("/health")
async def admin_health():
    """Admin health check"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00"}