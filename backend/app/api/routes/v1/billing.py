"""
Billing Routes
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

router = APIRouter()


@router.get("/subscription")
async def get_subscription():
    """Get user subscription"""
    return {
        "tier": "free",
        "status": "active",
        "features": ["basic_chat", "document_upload"]
    }


@router.get("/invoices")
async def get_invoices():
    """Get invoices"""
    return {"invoices": []}