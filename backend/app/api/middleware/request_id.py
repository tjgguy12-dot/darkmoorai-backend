"""
Request ID Middleware
Add unique ID to each request for tracing
"""

from fastapi import Request
import uuid

async def request_id_middleware(request: Request, call_next):
    """
    Add request ID to every request
    """
    # Get or generate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    
    # Store in request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response