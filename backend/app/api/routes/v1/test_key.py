"""
Test API Key Endpoint
"""

from fastapi import APIRouter
import os
from dotenv import load_dotenv

router = APIRouter()


@router.get("/test-key")
async def test_key():
    """Test if API key is loading correctly"""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    return {
        "key_preview": f"{api_key[:10]}...{api_key[-4:]}" if api_key else "None",
        "key_length": len(api_key),
        "starts_with_sk": api_key.startswith("sk-"),
        "loaded": bool(api_key)
    }