"""
Logging Middleware
Log all requests and responses
"""

from fastapi import Request
import time
import json
from typing import Optional

from app.utils.logger import logger
from app.monitoring.metrics import record_request

async def logging_middleware(request: Request, call_next):
    """
    Log all requests with timing and metadata
    """
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", generate_request_id())
    request.state.request_id = request_id
    
    # Log request
    await log_request(request)
    
    # Time the request
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        await log_response(request, response, duration)
        
        # Record metrics
        record_request(
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
            user_id=get_user_id(request)
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(f"Request failed: {e}", exc_info=True)
        raise

async def log_request(request: Request):
    """
    Log incoming request
    """
    # Don't log health checks
    if request.url.path.startswith("/api/v1/health"):
        return
    
    # Get request body for debugging (limit size)
    body = None
    if request.method in ["POST", "PUT"]:
        try:
            body_bytes = await request.body()
            if len(body_bytes) < 10000:  # Only log small requests
                body = body_bytes.decode()
        except:
            pass
    
    log_data = {
        "type": "request",
        "request_id": request.state.request_id,
        "method": request.method,
        "path": request.url.path,
        "query": str(request.query_params),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("User-Agent"),
        "user_id": get_user_id(request),
        "body_preview": body[:500] if body else None
    }
    
    logger.info(f"Incoming request: {json.dumps(log_data)}")

async def log_response(request: Request, response, duration: float):
    """
    Log outgoing response
    """
    # Don't log health checks
    if request.url.path.startswith("/api/v1/health"):
        return
    
    log_data = {
        "type": "response",
        "request_id": request.state.request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "user_id": get_user_id(request)
    }
    
    if response.status_code >= 400:
        logger.warning(f"Response: {json.dumps(log_data)}")
    else:
        logger.info(f"Response: {json.dumps(log_data)}")

def generate_request_id() -> str:
    """
    Generate unique request ID
    """
    import uuid
    return str(uuid.uuid4())

def get_user_id(request: Request) -> Optional[str]:
    """
    Get user ID from request state if available
    """
    if hasattr(request.state, "user"):
        return request.state.user.get("id")
    return None