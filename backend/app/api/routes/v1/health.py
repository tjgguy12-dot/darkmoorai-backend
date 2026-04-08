"""
Health Check Routes
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "darkmoorai-backend"
    }


@router.get("/info")
async def info():
    """Service info"""
    return {
        "name": "DarkmoorAI Backend",
        "version": "1.0.0",
        "description": "🧠 Intelligence, evolved",
        "environment": "development",
        "features": {
            "rag": True,
            "wikipedia": True,
            "arxiv": True,
            "document_upload": True,
            "streaming": True
        }
    }