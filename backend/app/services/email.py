"""
Email Service
Send emails for verification, password reset, notifications
"""

from typing import List, Dict, Any, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from pathlib import Path

from app.config import config
from app.utils.logger import logger

class EmailService:
    """
    Email sending service
    """
    
    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_pass = config.SMTP_PASS
        self.from_email = config.EMAIL_FROM
        
        self.templates_dir = Path("app/templates/emails")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send email using template
        """
        if not self.smtp_host:
            logger.warning("Email not configured, skipping send")
            return False
        
        try:
            # Load template
            html = await self._render_template(f"{template_name}.html", context)
            text = await self._render_template(f"{template_name}.txt", context)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to
            
            # Attach parts
            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))
            
            # Send
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_pass,
                use_tls=True
            )
            
            logger.info(f"Email sent to {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False
    
    async def send_verification_email(self, email: str, token: str):
        """
        Send email verification link
        """
        context = {
            "verification_url": f"{config.FRONTEND_URL}/verify-email?token={token}",
            "token": token
        }
        
        await self.send_email(
            to=email,
            subject="Verify your DarkmoorAI email",
            template_name="verification",
            context=context
        )
    
    async def send_password_reset_email(self, email: str, token: str):
        """
        Send password reset link
        """
        context = {
            "reset_url": f"{config.FRONTEND_URL}/reset-password?token={token}",
            "token": token
        }
        
        await self.send_email(
            to=email,
            subject="Reset your DarkmoorAI password",
            template_name="password_reset",
            context=context
        )
    
    async def send_welcome_email(self, email: str, name: str):
        """
        Send welcome email to new users
        """
        context = {
            "name": name,
            "dashboard_url": f"{config.FRONTEND_URL}/dashboard"
        }
        
        await self.send_email(
            to=email,
            subject="Welcome to DarkmoorAI! 🧠",
            template_name="welcome",
            context=context
        )
    
    async def send_usage_alert(self, email: str, usage: Dict[str, Any]):
        """
        Send usage alert email
        """
        context = {
            "usage": usage,
            "dashboard_url": f"{config.FRONTEND_URL}/billing"
        }
        
        await self.send_email(
            to=email,
            subject="DarkmoorAI Usage Alert",
            template_name="usage_alert",
            context=context
        )
    
    async def send_invoice_email(self, email: str, invoice: Dict[str, Any]):
        """
        Send invoice email
        """
        context = {
            "invoice": invoice,
            "dashboard_url": f"{config.FRONTEND_URL}/billing"
        }
        
        await self.send_email(
            to=email,
            subject=f"DarkmoorAI Invoice: ${invoice['amount']/100:.2f}",
            template_name="invoice",
            context=context
        )
    
    async def _render_template(self, template_name: str, context: Dict) -> str:
        """
        Render email template
        """
        template_path = self.templates_dir / template_name
        
        if template_path.exists():
            with open(template_path) as f:
                template = Template(f.read())
                return template.render(**context)
        
        # Return default template
        if template_name.endswith('.html'):
            return self._default_html_template(context)
        else:
            return self._default_text_template(context)
    
    def _default_html_template(self, context: Dict) -> str:
        """Default HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DarkmoorAI</title>
        </head>
        <body>
            <h1>🧠 DarkmoorAI</h1>
            <p>{context.get('message', '')}</p>
            <a href="{context.get('url', '#')}">{context.get('link_text', 'Click here')}</a>
        </body>
        </html>
        """
    
    def _default_text_template(self, context: Dict) -> str:
        """Default text template"""
        return f"""
        DarkmoorAI
        
        {context.get('message', '')}
        
        {context.get('url', '')}
        """