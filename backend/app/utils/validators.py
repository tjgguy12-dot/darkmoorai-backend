"""
Validators Module
Input validation functions
"""

import re
from typing import Optional, List
from pathlib import Path

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str, min_length: int = 8, max_length: int = 72) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    bcrypt has a hard limit of 72 bytes, so we enforce max_length.
    Returns (is_valid, error_message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > max_length:
        return False, f"Password must be at most {max_length} characters (bcrypt limit)"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    # Optional: require at least one special character
    # if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
    #     return False, "Password must contain at least one special character"
    
    return True, None

def validate_url(url: str) -> bool:
    """
    Validate URL format
    """
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?(?:/[-\w%!./?=&]*)?$'
    return bool(re.match(pattern, url))

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file type by extension
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be at most 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    """
    # Basic international phone validation
    pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{3,4}$'
    return bool(re.match(pattern, phone))

def validate_json_schema(data: dict, schema: dict) -> bool:
    """
    Validate JSON against schema
    """
    try:
        for field, field_type in schema.items():
            if field not in data:
                return False
            if not isinstance(data[field], field_type):
                return False
        return True
    except:
        return False

def validate_language_code(code: str) -> bool:
    """
    Validate language code (ISO 639-1)
    """
    return bool(re.match(r'^[a-z]{2}$', code))

def validate_color_hex(color: str) -> bool:
    """
    Validate hex color code
    """
    return bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color))

def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))