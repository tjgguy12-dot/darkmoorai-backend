"""
Metrics Middleware
Collect request metrics for monitoring
"""

from fastapi import Request
import time

from app.monitoring.metrics import (
    increment_requests_total,
    observe_request_duration,
    increment_errors_total
)

async def metrics_middleware(request: Request, call_next):
    """
    Collect metrics for every request
    """
    # Start timer
    start_time = time.time()
    
    # Process request
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        observe_request_duration(
            method=request.method,
            path=request.url.path,
            duration=duration
        )
        
        increment_requests_total(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        )
        
        # Record errors
        if response.status_code >= 400:
            increment_errors_total(
                method=request.method,
                path=request.url.path,
                status=response.status_code
            )
        
        return response
        
    except Exception as e:
        # Record error metric
        increment_errors_total(
            method=request.method,
            path=request.url.path,
            status=500
        )
        raise