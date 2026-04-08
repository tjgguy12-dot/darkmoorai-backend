"""
Utils Package
Utility functions and helpers
"""

from .logger import setup_logging, get_logger, logger
from .exceptions import (
    DarkmoorError, ValidationError, NotFoundError, 
    AuthenticationError, PermissionError, RateLimitError,
    DocumentProcessingError, AIProviderError, QuotaExceededError
)
from .helpers import (
    generate_id, parse_date, format_size, truncate_text,
    safe_json_loads, safe_json_dumps, get_client_ip
)
from .validators import validate_email, validate_password, validate_url, validate_file_type
from .encryption import encrypt, decrypt, hash_string, verify_hash
from .dates import format_datetime, parse_datetime, get_time_ago