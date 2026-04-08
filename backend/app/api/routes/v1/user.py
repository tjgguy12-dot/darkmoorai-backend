"""
User Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()


@router.get("/profile")
async def get_profile():
    """Get user profile"""
    return {
        "id": "test-user-123",
        "email": "test@darkmoor.ai",
        "username": "testuser",
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
        "is_verified": True,
        "created_at": "2024-01-01T00:00:00",
        "total_messages": 0,
        "total_documents": 0,
        "settings": {
            "theme": "dark",
            "language": "en"
        }
    }


@router.get("/settings")
async def get_settings():
    """Get user settings"""
    return {
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True,
        "search_sources": ["wikipedia", "arxiv", "pubmed"]
    }


@router.get("/api-keys")
async def get_api_keys():
    """Get API keys"""
    return []


@router.get("/usage")
async def get_usage():
    """Get usage stats"""
    return {
        "daily": {
            "date": "2024-01-01",
            "cost": 0.0,
            "budget": 0.10,
            "remaining": 0.10,
            "percentage": 0
        },
        "monthly": {
            "month": "2024-01",
            "cost": 0.0,
            "projected": 0.0
        },
        "tokens_today": 0,
        "budget_remaining": True
    }