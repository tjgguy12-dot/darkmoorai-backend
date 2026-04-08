"""
Logging Module
Structured logging with Loguru
"""

import sys
import json
from pathlib import Path
from loguru import logger
from datetime import datetime

from app.config import config

# Remove default handler
logger.remove()

# Console handler (colored)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if config.DEBUG else "INFO",
    colorize=True
)

# Ensure log directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# File handler - all logs (rotating)
logger.add(
    log_dir / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="100 MB",
    retention="30 days",
    compression="gz",
    level="INFO"
)

# File handler - errors only
logger.add(
    log_dir / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="100 MB",
    retention="90 days",
    compression="gz",
    level="ERROR"
)

# JSON structured logs – FIXED (raw sink, no formatting conflict)
def json_sink(message):
    """Write JSON logs directly without loguru formatting interference"""
    record = message.record
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "request_id": record.get("extra", {}).get("request_id"),
        "user_id": record.get("extra", {}).get("user_id")
    }
    with open(log_dir / "structured.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

logger.add(
    json_sink,
    level="INFO"
)

def setup_logging():
    """Setup logging configuration"""
    logger.info(f"Logging configured. Environment: {config.ENV}")

def get_logger(name: str):
    """Get logger with module name"""
    return logger.bind(name=name)

# Global logger instance
__all__ = ["logger", "setup_logging", "get_logger"]