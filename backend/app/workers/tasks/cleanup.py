"""
Cleanup Tasks
Background cleanup of old files and data
"""

from celery import shared_task
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from app.config import config
from app.database.repositories.token_repo import TokenRepository
from app.utils.logger import logger

@shared_task(name='cleanup_old_files')
def cleanup_old_files(days: int = 30):
    """
    Clean up old temporary files
    """
    upload_dir = config.UPLOAD_DIR / "temp"
    cutoff = datetime.now() - timedelta(days=days)
    
    deleted = 0
    errors = 0
    
    for item in upload_dir.glob('*'):
        if item.is_file():
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff:
                    item.unlink()
                    deleted += 1
            except Exception as e:
                logger.error(f"Failed to delete {item}: {e}")
                errors += 1
    
    logger.info(f"Cleaned up {deleted} old files, {errors} errors")
    
    return {
        'deleted': deleted,
        'errors': errors,
        'days_threshold': days
    }

@shared_task(name='cleanup_expired_tokens')
def cleanup_expired_tokens():
    """
    Clean up expired authentication tokens
    """
    token_repo = TokenRepository()
    now = datetime.utcnow().isoformat()
    
    # This would need actual DB queries
    # Simplified for now
    
    return {
        'tokens_removed': 0
    }

@shared_task(name='cleanup_old_vector_chunks')
def cleanup_old_vector_chunks(days: int = 90):
    """
    Clean up old vector chunks from deleted documents
    """
    from app.document_processor.vector_store import vector_store
    
    # Vector store cleanup would happen here
    # This is a placeholder
    
    return {
        'status': 'not_implemented'
    }

@shared_task(name='cleanup_old_logs')
def cleanup_old_logs(days: int = 30):
    """
    Clean up old log files
    """
    log_dir = Path("logs")
    cutoff = datetime.now() - timedelta(days=days)
    
    deleted = 0
    
    for log_file in log_dir.glob('*.log*'):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                log_file.unlink()
                deleted += 1
        except Exception as e:
            logger.error(f"Failed to delete log {log_file}: {e}")
    
    return {'deleted': deleted}