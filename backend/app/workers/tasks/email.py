"""
Email Tasks
Background email sending
"""

from celery import shared_task
from app.services.email import EmailService
from app.utils.logger import logger

@shared_task(bind=True, name='send_bulk_email')
def send_bulk_email(self, emails: list, template: str, context: dict):
    """
    Send bulk emails
    """
    email_service = EmailService()
    results = []
    
    total = len(emails)
    
    for i, email in enumerate(emails):
        try:
            # Update progress
            progress = int((i + 1) / total * 100)
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'current': i + 1, 'total': total}
            )
            
            # Send email
            success = email_service.send_email(
                to=email,
                subject=context.get('subject', ''),
                template_name=template,
                context=context
            )
            
            results.append({
                'email': email,
                'success': success
            })
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            results.append({
                'email': email,
                'success': False,
                'error': str(e)
            })
    
    return {
        'status': 'completed',
        'total': total,
        'successful': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success']),
        'results': results
    }

@shared_task(name='send_welcome_email')
def send_welcome_email(user_email: str, user_name: str):
    """
    Send welcome email to new user
    """
    email_service = EmailService()
    
    context = {
        'name': user_name,
        'dashboard_url': 'https://app.darkmoor.ai/dashboard'
    }
    
    success = email_service.send_email(
        to=user_email,
        subject='Welcome to DarkmoorAI! 🧠',
        template_name='welcome',
        context=context
    )
    
    return {'success': success}

@shared_task(name='send_usage_report')
def send_usage_report(user_email: str, report_data: dict):
    """
    Send usage report email
    """
    email_service = EmailService()
    
    success = email_service.send_email(
        to=user_email,
        subject='Your DarkmoorAI Usage Report',
        template_name='usage_report',
        context=report_data
    )
    
    return {'success': success}