"""
DarkmoorAI Main Application
Complete with Office Suite Integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import config
from app.api.routes.v1 import (
    auth_router,
    chat_router,
    documents_router,
    search_router,
    user_router,
    admin_router,
    billing_router,
    webhooks_router,
    health_router,
    office_router
)
from app.database.session import init_db, close_db
from app.core.cache import init_cache, close_cache
from app.monitoring.metrics import setup_metrics
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Debug print
print("=" * 60)
print("🧠 DARKMOORAI BACKEND STARTING...")
print("=" * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("🚀 DarkmoorAI starting up...")
    await init_db()
    await init_cache()
    setup_metrics()
    logger.info("✅ DarkmoorAI ready to serve!")
    
    yield
    
    # Shutdown
    logger.info("🛑 DarkmoorAI shutting down...")
    await close_db()
    await close_cache()
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="DarkmoorAI API",
    description="🧠 Intelligence, evolved - Complete AI Assistant with Office Suite",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Include all routers
# ============================================================================

# Core API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(user_router, prefix="/api/v1/user", tags=["User"])
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])

# Office Suite routers
app.include_router(office_router, prefix="/api/v1/office", tags=["Office Suite"])
print("✅ Office router added to app!")

# Admin and billing (optional)
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(webhooks_router, prefix="/api/v1/webhooks", tags=["Webhooks"])

# Print registered routes for debugging
print("\n" + "=" * 60)
print("📋 REGISTERED ROUTES:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"  {route.path}")
print("=" * 60 + "\n")


# ============================================================================
# Root endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "DarkmoorAI",
        "version": "2.0.0",
        "status": "operational",
        "message": "🧠 Intelligence, evolved",
        "features": {
            "chat": True,
            "rag": True,
            "document_processing": True,
            "office_suite": True,
            "web_search": True,
            "research_mode": True
        },
        "endpoints": {
            "docs": "/docs",
            "api": "/api/v1",
            "office": "/api/v1/office",
            "health": "/api/v1/health"
        }
    }


@app.get("/api/v1")
async def api_root():
    """API root endpoint with available modules"""
    return {
        "name": "DarkmoorAI API",
        "version": "2.0.0",
        "modules": {
            "auth": "/api/v1/auth",
            "chat": "/api/v1/chat",
            "documents": "/api/v1/documents",
            "search": "/api/v1/search",
            "user": "/api/v1/user",
            "office": "/api/v1/office",
            "health": "/api/v1/health"
        },
        "documentation": "/docs"
    }


# ============================================================================
# Office Suite info endpoint (redundant but kept for convenience)
# ============================================================================

@app.get("/api/v1/office-info")
async def office_info_alt():
    """Alternate Office Suite info endpoint"""
    return {
        "name": "DarkmoorAI Office Suite",
        "version": "1.0.0",
        "description": "Free office document creation and editing suite",
        "features": {
            "word": {
                "create": True,
                "edit": True,
                "templates": ["invoice", "report", "resume", "business_letter"],
                "formats": [".docx", ".pdf", ".txt"]
            },
            "excel": {
                "create": True,
                "edit": True,
                "formulas": True,
                "charts": ["bar", "line", "pie"],
                "templates": ["budget"],
                "formats": [".xlsx", ".csv"]
            }
        },
        "templates_available": ["invoice", "resume", "report", "business_letter", "budget"],
        "cost": "Free"
    }


# ============================================================================
# Error handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )