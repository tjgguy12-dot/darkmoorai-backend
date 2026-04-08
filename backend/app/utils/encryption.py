"""
Encryption Module
Data encryption and hashing utilities
"""

import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from app.config import config

# Get encryption key from environment or generate one
ENCRYPTION_KEY = getattr(config, 'ENCRYPTION_KEY', None)

if ENCRYPTION_KEY:
    # Convert string key to bytes if needed
    if isinstance(ENCRYPTION_KEY, str):
        ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
    fernet = Fernet(ENCRYPTION_KEY)
else:
    # Generate temporary key (for development only)
    fernet = Fernet(Fernet.generate_key())

def encrypt(data: str) -> str:
    """
    Encrypt data using Fernet symmetric encryption
    """
    if not data:
        return data
    
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()

def decrypt(data: str) -> str:
    """
    Decrypt data using Fernet symmetric encryption
    """
    if not data:
        return data
    
    try:
        decrypted = fernet.decrypt(data.encode())
        return decrypted.decode()
    except:
        return data

def hash_string(data: str, salt: str = None) -> str:
    """
    Hash string with SHA-256
    """
    if not salt:
        salt = secrets.token_hex(16)
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        data.encode(),
        salt.encode(),
        100000,
        dklen=32
    )
    
    return f"{salt}:{base64.b64encode(key).decode()}"

def verify_hash(data: str, hash_string: str) -> bool:
    """
    Verify hash against string
    """
    try:
        salt, key = hash_string.split(':')
        new_hash = hash_string(data, salt)
        return new_hash == hash_string
    except:
        return False

def generate_api_key() -> str:
    """
    Generate secure API key
    """
    return f"dm_{secrets.token_urlsafe(32)}"

def generate_secret(length: int = 32) -> str:
    """
    Generate secure random secret
    """
    return secrets.token_urlsafe(length)

def mask_sensitive(data: str, visible_start: int = 4, visible_end: int = 4) -> str:
    """
    Mask sensitive data (e.g., API keys)
    """
    if len(data) <= visible_start + visible_end:
        return '*' * 8
    
    return data[:visible_start] + '*' * (len(data) - visible_start - visible_end) + data[-visible_end:]

def sanitize_data(data: dict, sensitive_fields: list) -> dict:
    """
    Remove sensitive fields from dictionary
    """
    result = data.copy()
    for field in sensitive_fields:
        if field in result:
            result[field] = '[REDACTED]'
    return result