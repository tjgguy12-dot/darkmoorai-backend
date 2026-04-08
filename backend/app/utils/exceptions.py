"""
Exceptions Module
Custom exceptions for DarkmoorAI
"""

class DarkmoorError(Exception):
    """Base exception for DarkmoorAI"""
    def __init__(self, message: str, code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class ValidationError(DarkmoorError):
    """Validation error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code=400, details=details)

class NotFoundError(DarkmoorError):
    """Resource not found error"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, code=404)

class AuthenticationError(DarkmoorError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code=401)

class PermissionError(DarkmoorError):
    """Permission denied error"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code=403)

class RateLimitError(DarkmoorError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code=429)

class DocumentProcessingError(DarkmoorError):
    """Document processing error"""
    def __init__(self, message: str, document_id: str = None):
        super().__init__(message, code=422)
        self.document_id = document_id

class AIProviderError(DarkmoorError):
    """AI provider error"""
    def __init__(self, message: str, provider: str = "deepseek"):
        super().__init__(message, code=503)
        self.provider = provider

class QuotaExceededError(DarkmoorError):
    """User quota exceeded error"""
    def __init__(self, message: str = "Quota exceeded"):
        super().__init__(message, code=429)