"""
Helpers Module
General utility functions
"""

import uuid
import json
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

def generate_id(prefix: str = "") -> str:
    """
    Generate unique ID
    """
    uid = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}_{uid}"
    return uid

def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string to datetime
    """
    try:
        return datetime.fromisoformat(date_string)
    except:
        return None

def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncate text to maximum length
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:
        truncated = truncated[:last_space]
    
    if add_ellipsis:
        truncated += '...'
    
    return truncated

def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON data
    """
    try:
        return json.loads(data)
    except:
        return default

def safe_json_dumps(data: Any, default: Any = None) -> str:
    """
    Safely dump JSON data
    """
    try:
        return json.dumps(data)
    except:
        return default if default is not None else "{}"

def get_client_ip(request) -> str:
    """
    Get client IP from request
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    """
    import re
    # Remove path separators and other dangerous characters
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:255 - len(ext)] + ext
    return filename

def dict_merge(a: dict, b: dict) -> dict:
    """
    Deep merge two dictionaries
    """
    result = a.copy()
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = value
    return result

def chunk_list(lst: list, size: int) -> list:
    """
    Split list into chunks
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def retry_async(func, retries: int = 3, delay: float = 1.0):
    """
    Retry decorator for async functions
    """
    import asyncio
    
    async def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
        raise last_error
    return wrapper