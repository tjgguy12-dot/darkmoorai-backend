"""
Queue Service
Background task management with Celery
"""

from typing import Dict, Any, Optional
from celery import Celery
from celery.result import AsyncResult
import asyncio

from app.config import config
from app.utils.logger import logger

# Initialize Celery
celery_app = Celery(
    'darkmoorai',
    broker=config.REDIS_URL,
    backend=config.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

class QueueService:
    """
    Background task queue service
    """
    
    @staticmethod
    async def send_task(task_name: str, args: list = None, kwargs: dict = None) -> str:
        """
        Send task to queue
        """
        args = args or []
        kwargs = kwargs or {}
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: celery_app.send_task(task_name, args=args, kwargs=kwargs)
        )
        
        logger.info(f"Task sent: {task_name} - {result.id}")
        
        return result.id
    
    @staticmethod
    async def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task result
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: AsyncResult(task_id, app=celery_app)
        )
        
        if result.ready():
            if result.successful():
                return {
                    'status': 'success',
                    'result': result.result
                }
            else:
                return {
                    'status': 'failed',
                    'error': str(result.result)
                }
        else:
            return {
                'status': 'pending',
                'progress': result.info.get('progress', 0) if result.info else 0
            }
    
    @staticmethod
    async def revoke_task(task_id: str):
        """
        Revoke/cancel task
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: celery_app.control.revoke(task_id, terminate=True)
        )
        
        logger.info(f"Task revoked: {task_id}")

# Celery tasks (defined here but imported by workers)

@celery_app.task(bind=True, name='process_document')
def process_document_task(self, document_id: str, user_id: str):
    """
    Process document in background
    """
    from app.document_processor.processor import DocumentProcessor
    
    processor = DocumentProcessor()
    
    try:
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Process document
        result = processor.process(document_id, user_id)
        
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        return {
            'status': 'success',
            'document_id': document_id,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_bulk_email')
def send_bulk_email_task(self, emails: list, template: str, context: dict):
    """
    Send bulk emails
    """
    from app.services.email import EmailService
    
    email_service = EmailService()
    results = []
    
    for i, email in enumerate(emails):
        try:
            success = email_service.send_email(
                to=email,
                subject=context.get('subject', ''),
                template_name=template,
                context=context
            )
            results.append({'email': email, 'success': success})
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'progress': int((i + 1) / len(emails) * 100)}
            )
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            results.append({'email': email, 'success': False, 'error': str(e)})
    
    return {
        'status': 'completed',
        'total': len(emails),
        'successful': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success']),
        'results': results
    }

@celery_app.task(name='cleanup_old_files')
def cleanup_old_files_task(days: int = 30):
    """
    Clean up old temporary files
    """
    from pathlib import Path
    import shutil
    from datetime import datetime, timedelta
    
    upload_dir = Path("data/uploads/temp")
    cutoff = datetime.now() - timedelta(days=days)
    
    deleted = 0
    for item in upload_dir.glob('*'):
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                item.unlink()
                deleted += 1
    
    logger.info(f"Cleaned up {deleted} old files")
    
    return {'deleted': deleted}

@celery_app.task(name='generate_usage_report')
def generate_usage_report_task(period: str = 'daily'):
    """
    Generate usage report
    """
    from app.services.analytics import AnalyticsService
    
    analytics = AnalyticsService()
    
    if period == 'daily':
        report = analytics.generate_daily_report()
    elif period == 'weekly':
        report = analytics.generate_weekly_report()
    elif period == 'monthly':
        report = analytics.generate_monthly_report()
    else:
        raise ValueError(f"Invalid period: {period}")
    
    return report