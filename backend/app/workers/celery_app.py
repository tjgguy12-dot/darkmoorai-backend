"""
Celery Application
Background task worker configuration
"""

from celery import Celery
from celery.schedules import crontab
import os

from app.config import config

# Create Celery app
celery_app = Celery(
    'darkmoorai',
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=[
        'app.workers.tasks.document',
        'app.workers.tasks.email',
        'app.workers.tasks.cleanup',
        'app.workers.tasks.billing',
        'app.workers.tasks.analytics'
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'app.workers.tasks.cleanup.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
        'args': (30,)
    },
    'generate-daily-report': {
        'task': 'app.workers.tasks.analytics.generate_daily_report',
        'schedule': crontab(hour=1, minute=0),  # Run at 1 AM daily
    },
    'process-invoices': {
        'task': 'app.workers.tasks.billing.process_invoices',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    'send-usage-alerts': {
        'task': 'app.workers.tasks.billing.send_usage_alerts',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
    'cleanup-expired-tokens': {
        'task': 'app.workers.tasks.cleanup.cleanup_expired_tokens',
        'schedule': crontab(hour=4, minute=0),  # Run at 4 AM daily
    },
}

if __name__ == '__main__':
    celery_app.start()