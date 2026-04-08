"""
Compression Middleware
Compress responses to save bandwidth
"""

from fastapi import Request
from fastapi.responses import Response
import gzip
import brotli

async def compression_middleware(request: Request, call_next):
    """
    Compress responses based on Accept-Encoding header
    """
    # Get accepted encodings
    accept_encoding = request.headers.get("Accept-Encoding", "")
    
    # Process request
    response = await call_next(request)
    
    # Skip compression for small responses
    if len(response.body) < 1024:  # 1KB
        return response
    
    # Skip for images, videos, etc.
    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith(("image/", "video/", "audio/")):
        return response
    
    # Compress based on accepted encoding
    if "br" in accept_encoding and len(response.body) > 1024:
        return compress_brotli(response)
    elif "gzip" in accept_encoding:
        return compress_gzip(response)
    
    return response

def compress_gzip(response: Response) -> Response:
    """Compress with gzip"""
    compressed = gzip.compress(response.body)
    
    return Response(
        content=compressed,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

def compress_brotli(response: Response) -> Response:
    """Compress with brotli"""
    compressed = brotli.compress(response.body)
    
    return Response(
        content=compressed,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )