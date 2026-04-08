#!/usr/bin/env python3
"""
Database Backup Script
Backup PostgreSQL database
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.config import config
from app.utils.logger import logger

def backup_database():
    """
    Backup database to file
    """
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"darkmoor_{timestamp}.sql"
    
    # Build pg_dump command
    cmd = [
        "pg_dump",
        f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}",
        "-f", str(backup_file),
        "-F", "c",  # Custom format
        "-v"
    ]
    
    logger.info(f"Starting backup to {backup_file}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Backup completed: {backup_file}")
        
        # Compress backup
        import gzip
        with open(backup_file, 'rb') as f_in:
            with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                f_out.writelines(f_in)
        
        backup_file.unlink()  # Remove uncompressed
        logger.info(f"Backup compressed: {backup_file}.gz")
        
        # Clean old backups (keep last 30 days)
        cleanup_old_backups(backup_dir, days=30)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        sys.exit(1)

def cleanup_old_backups(backup_dir: Path, days: int):
    """
    Delete backups older than specified days
    """
    import time
    cutoff = time.time() - (days * 24 * 3600)
    
    for backup in backup_dir.glob("darkmoor_*.sql.gz"):
        if backup.stat().st_mtime < cutoff:
            backup.unlink()
            logger.info(f"Deleted old backup: {backup}")

if __name__ == "__main__":
    backup_database()