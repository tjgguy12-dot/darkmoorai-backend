"""
Email Service for Sending OTPs and Notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import asyncio

from app.config import config
from app.utils.logger import logger


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASS
        self.from_email = config.EMAIL_FROM
        self.from_name = getattr(config, 'SMTP_FROM_NAME', 'DarkmoorAI')
        
    async def send_otp_email(self, email: str, otp_code: str) -> bool:
        """
        Send OTP verification code to user's email
        """
        subject = "🔐 DarkmoorAI - Email Verification Code"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; 
                             padding: 20px; background: white; border-radius: 10px; 
                             letter-spacing: 5px; font-family: monospace; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 DarkmoorAI</h1>
                    <p>Verify Your Email Address</p>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Thank you for registering with DarkmoorAI! Please use the verification code below to complete your registration:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p>This code will expire in <strong>10 minutes</strong>.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <hr>
                    <p><strong>Security Tip:</strong> Never share this code with anyone.</p>
                </div>
                <div class="footer">
                    <p>© 2025 DarkmoorAI - Intelligence, Evolved</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        DarkmoorAI - Email Verification
        
        Your verification code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        """
        
        return await self._send_email(email, subject, html_body, text_body)
    
    async def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Send email using SMTP"""
        
        # For development, just print to console
        if config.ENV == "development" and not self.smtp_host:
            logger.info(f"📧 [DEV MODE] Email would be sent to: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body preview: {text_body[:200]}...")
            return True
        
        if not self.smtp_host or not self.smtp_user:
            logger.error("SMTP not configured. Cannot send email.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email or self.smtp_user}>"
            msg['To'] = to_email
            
            # Attach both plain text and HTML versions
            part_text = MIMEText(text_body, 'plain')
            part_html = MIMEText(html_body, 'html')
            msg.attach(part_text)
            msg.attach(part_html)
            
            # Send email in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_smtp,
                msg,
                to_email
            )
            
            logger.info(f"✅ OTP email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _send_smtp(self, msg, to_email: str):
        """Synchronous SMTP sending"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            raise
    
    async def send_password_reset_email(self, email: str, reset_token: str):
        """Send password reset email"""
        subject = "🔐 DarkmoorAI - Password Reset Request"
        
        frontend_url = getattr(config, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .button {{ background: #667eea; color: white; padding: 12px 24px; 
                           text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>DarkmoorAI</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"Reset your DarkmoorAI password: {reset_link}"
        
        await self._send_email(email, subject, html_body, text_body)


# Global instance
email_service = EmailService()