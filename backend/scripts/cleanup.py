#!/usr/bin/env python3
"""
Cleanup Script
Remove old temporary files and data
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from app.config import config
from app.utils.logger import logger

async def cleanup_temp_files():
    """
    Clean up old temporary files
    """
    upload_dir = config.UPLOAD_DIR / "temp"
    cutoff = datetime.now() - timedelta(days=1)
    
    deleted = 0
    
    for file_path in upload_dir.glob("*"):
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                file_path.unlink()
                deleted += 1
                logger.debug(f"Deleted: {file_path}")
    
    logger.info(f"Deleted {deleted} old temp files")

async def cleanup_old_logs():
    """
    Clean up old log files
    """
    log_dir = Path("logs")
    cutoff = datetime.now() - timedelta(days=30)
    
    deleted = 0
    
    for log_file in log_dir.glob("*.log*"):
        if log_file.is_file():
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                log_file.unlink()
                deleted += 1
                logger.debug(f"Deleted: {log_file}")
    
    logger.info(f"Deleted {deleted} old log files")

async def main():
    """
    Run all cleanup tasks
    """
    logger.info("Starting cleanup...")
    
    await cleanup_temp_files()
    await cleanup_old_logs()
    
    logger.info("Cleanup completed")

if __name__ == "__main__":
    asyncio.run(main())