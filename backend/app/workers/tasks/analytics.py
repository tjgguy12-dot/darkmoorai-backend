"""
Analytics Tasks
Background analytics and reporting
"""

from celery import shared_task
from datetime import datetime, timedelta
import json

from app.services.analytics import AnalyticsService
from app.services.email import EmailService
from app.database.repositories.user_repo import UserRepository
from app.utils.logger import logger

analytics_service = AnalyticsService()
email_service = EmailService()
user_repo = UserRepository()

@shared_task(name='generate_daily_report')
def generate_daily_report():
    """
    Generate daily analytics report
    """
    logger.info("Generating daily analytics report")
    
    try:
        report = analytics_service.generate_daily_report()
        
        # Send to admin email if configured
        if email_service.smtp_host:
            email_service.send_email(
                to="admin@darkmoor.ai",
                subject=f"DarkmoorAI Daily Report - {report['date']}",
                template_name="admin_daily_report",
                context={"report": report}
            )
        
        # Store report
        from app.database.repositories.report_repo import ReportRepository
        repo = ReportRepository()
        await repo.create({
            "type": "daily",
            "date": report['date'],
            "data": report,
            "created_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Daily report generated: {report['date']}")
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        return {"error": str(e)}

@shared_task(name='generate_weekly_report')
def generate_weekly_report():
    """
    Generate weekly analytics report
    """
    logger.info("Generating weekly analytics report")
    
    try:
        report = analytics_service.generate_weekly_report()
        
        # Send to admin email
        if email_service.smtp_host:
            email_service.send_email(
                to="admin@darkmoor.ai",
                subject=f"DarkmoorAI Weekly Report - {report['week_start']} to {report['week_end']}",
                template_name="admin_weekly_report",
                context={"report": report}
            )
        
        logger.info("Weekly report generated")
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {e}")
        return {"error": str(e)}

@shared_task(name='generate_monthly_report')
def generate_monthly_report():
    """
    Generate monthly analytics report
    """
    logger.info("Generating monthly analytics report")
    
    try:
        report = analytics_service.generate_monthly_report()
        
        # Send to admin email
        if email_service.smtp_host:
            email_service.send_email(
                to="admin@darkmoor.ai",
                subject=f"DarkmoorAI Monthly Report - {report['month_start']} to {report['month_end']}",
                template_name="admin_monthly_report",
                context={"report": report}
            )
        
        logger.info("Monthly report generated")
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate monthly report: {e}")
        return {"error": str(e)}

@shared_task(name='aggregate_hourly_metrics')
def aggregate_hourly_metrics():
    """
    Aggregate hourly system metrics
    """
    from app.monitoring.metrics import get_metrics_snapshot
    
    metrics = get_metrics_snapshot()
    
    # Store in database for long-term retention
    from app.database.repositories.metric_repo import MetricRepository
    repo = MetricRepository()
    await repo.create({
        "timestamp": datetime.utcnow().isoformat(),
        "interval": "hourly",
        "metrics": metrics
    })
    
    return {"status": "success"}

@shared_task(name='track_user_retention')
def track_user_retention():
    """
    Calculate and track user retention metrics
    """
    retention = analytics_service._calculate_retention()
    
    # Store retention metrics
    from app.database.repositories.retention_repo import RetentionRepository
    repo = RetentionRepository()
    await repo.create({
        "date": datetime.utcnow().date().isoformat(),
        "retention": retention
    })
    
    return retention