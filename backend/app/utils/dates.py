"""
Dates Module
Date and time utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import pytz

def format_datetime(
    dt: Optional[datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone: str = "UTC"
) -> str:
    """
    Format datetime to string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(tz)
    
    return dt.strftime(format_str)

def parse_datetime(
    dt_string: str,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse datetime from string
    """
    try:
        return datetime.strptime(dt_string, format_str)
    except:
        return None

def get_time_ago(
    dt: datetime,
    now: Optional[datetime] = None
) -> str:
    """
    Get human-readable time ago string
    """
    if now is None:
        now = datetime.utcnow()
    
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(diff.days / 365)
        return f"{years} year{'s' if years != 1 else ''} ago"

def get_date_range(days: int) -> tuple[datetime, datetime]:
    """
    Get date range from N days ago to now
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return start, end

def is_expired(expires_at: Union[str, datetime], now: Optional[datetime] = None) -> bool:
    """
    Check if token/document is expired
    """
    if isinstance(expires_at, str):
        expires_at = parse_datetime(expires_at)
    
    if not expires_at:
        return True
    
    if now is None:
        now = datetime.utcnow()
    
    return now > expires_at

def get_days_until(expires_at: Union[str, datetime]) -> int:
    """
    Get days until expiration
    """
    if isinstance(expires_at, str):
        expires_at = parse_datetime(expires_at)
    
    if not expires_at:
        return 0
    
    now = datetime.utcnow()
    diff = expires_at - now
    
    return max(0, diff.days)

def to_iso(dt: datetime) -> str:
    """
    Convert datetime to ISO format
    """
    return dt.isoformat()

def from_iso(iso_string: str) -> Optional[datetime]:
    """
    Parse ISO datetime string
    """
    try:
        return datetime.fromisoformat(iso_string)
    except:
        return None