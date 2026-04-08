"""
API v1 routes
"""
from .auth import router as auth_router
from .chat import router as chat_router
from .documents import router as documents_router
from .search import router as search_router
from .user import router as user_router
from .health import router as health_router
from .office import router as office_router

# Optional routers - create if they exist, otherwise use placeholder
try:
    from .admin import router as admin_router
except ImportError:
    from fastapi import APIRouter
    admin_router = APIRouter()
    @admin_router.get("/")
    async def admin_placeholder():
        return {"message": "Admin routes coming soon"}

try:
    from .billing import router as billing_router
except ImportError:
    from fastapi import APIRouter
    billing_router = APIRouter()
    @billing_router.get("/")
    async def billing_placeholder():
        return {"message": "Billing routes coming soon"}

try:
    from .webhooks import router as webhooks_router
except ImportError:
    from fastapi import APIRouter
    webhooks_router = APIRouter()
    @webhooks_router.get("/")
    async def webhooks_placeholder():
        return {"message": "Webhook routes coming soon"}

__all__ = [
    "auth_router",
    "chat_router",
    "documents_router",
    "search_router",
    "user_router",
    "health_router",
    "office_router",
    "admin_router",
    "billing_router",
    "webhooks_router"
]