"""
Error Handler Middleware
Centralized error handling and formatting
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union, Dict, Any
import traceback

from app.utils.logger import logger
from app.config import config

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global error handler for all exceptions
    """
    # Log the error
    log_error(request, exc)
    
    # Handle HTTP exceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "http_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle validation errors
    if hasattr(exc, "errors"):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "type": "validation_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle database errors
    if "database" in str(exc).lower() or "sql" in str(exc).lower():
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": 503,
                    "message": "Database service unavailable",
                    "type": "database_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle rate limit errors
    if "rate limit" in str(exc).lower():
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": 429,
                    "message": "Too many requests",
                    "type": "rate_limit_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle authentication errors
    if "authentication" in str(exc).lower() or "auth" in str(exc).lower():
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": 401,
                    "message": "Authentication failed",
                    "type": "auth_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle authorization errors
    if "authorization" in str(exc).lower() or "permission" in str(exc).lower():
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": 403,
                    "message": "Permission denied",
                    "type": "permission_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle file upload errors
    if "file" in str(exc).lower():
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": 400,
                    "message": str(exc),
                    "type": "file_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle AI service errors
    if "deepseek" in str(exc).lower() or "ai" in str(exc).lower():
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": 503,
                    "message": "AI service temporarily unavailable",
                    "type": "ai_service_error"
                },
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Handle all other errors (500 Internal Server Error)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "server_error",
                "debug": str(exc) if config.DEBUG else None
            },
            "request_id": getattr(request.state, "request_id", None)
        }
    )

def log_error(request: Request, exc: Exception):
    """
    Log error with context
    """
    error_data = {
        "request_id": getattr(request.state, "request_id", None),
        "method": request.method,
        "path": request.url.path,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "user_id": get_user_id(request),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("User-Agent")
    }
    
    # Add traceback for 500 errors
    if not isinstance(exc, HTTPException) or exc.status_code >= 500:
        error_data["traceback"] = traceback.format_exc()
        logger.error(f"Unhandled exception: {error_data}", exc_info=True)
    else:
        logger.warning(f"HTTP exception: {error_data}")

def get_user_id(request: Request) -> str:
    """
    Get user ID from request state
    """
    if hasattr(request.state, "user"):
        return request.state.user.get("id")
    return "anonymous"