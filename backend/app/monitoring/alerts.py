"""
Alerts Module
System alert management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

from app.config import config
from app.utils.logger import logger

class AlertManager:
    """
    Manage system alerts and notifications
    """
    
    def __init__(self):
        self.alerts = []
        self.slack_webhook = getattr(config, 'SLACK_WEBHOOK_URL', None)
        self.sentry_dsn = getattr(config, 'SENTRY_DSN', None)
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        metadata: Optional[Dict] = None
    ):
        """
        Send alert to configured channels
        """
        alert = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        logger.warning(f"ALERT [{severity}]: {title} - {message}")
        
        # Store alert
        self.alerts.append(alert)
        
        # Send to Slack if configured
        if self.slack_webhook:
            await self._send_to_slack(alert)
        
        # Send to Sentry if configured
        if self.sentry_dsn and severity == "error":
            await self._send_to_sentry(alert)
    
    async def _send_to_slack(self, alert: Dict[str, Any]):
        """Send alert to Slack"""
        try:
            color = {
                "info": "#36a64f",
                "warning": "#ffcc00",
                "error": "#ff0000",
                "critical": "#990000"
            }.get(alert["severity"], "#36a64f")
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": alert["title"],
                    "text": alert["message"],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert["severity"],
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert["timestamp"],
                            "short": True
                        }
                    ],
                    "footer": "DarkmoorAI Monitoring"
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(self.slack_webhook, json=payload)
                
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_to_sentry(self, alert: Dict[str, Any]):
        """Send alert to Sentry"""
        try:
            import sentry_sdk
            sentry_sdk.capture_message(
                f"{alert['title']}: {alert['message']}",
                level=alert["severity"]
            )
        except Exception as e:
            logger.error(f"Failed to send Sentry alert: {e}")
    
    async def check_thresholds(self):
        """
        Check system thresholds and trigger alerts
        """
        from app.monitoring.metrics import get_metrics_snapshot
        
        metrics = get_metrics_snapshot()
        
        # Check error rate
        total_requests = metrics.get("requests_total", 0)
        total_errors = metrics.get("errors_total", 0)
        
        if total_requests > 100 and total_errors / total_requests > 0.05:
            await self.send_alert(
                title="High Error Rate",
                message=f"Error rate is {total_errors / total_requests * 100:.2f}%",
                severity="warning",
                metadata={"error_rate": total_errors / total_requests}
            )
        
        # Check API costs
        cost_total = metrics.get("cost_total", 0)
        if cost_total > 100:  # $100 threshold
            await self.send_alert(
                title="High API Costs",
                message=f"Total API costs: ${cost_total:.2f}",
                severity="warning",
                metadata={"cost": cost_total}
            )
        
        # Check queue size
        queue_size = metrics.get("queue_size", 0)
        if queue_size > 1000:
            await self.send_alert(
                title="Large Queue Size",
                message=f"Queue size is {queue_size}",
                severity="warning",
                metadata={"queue_size": queue_size}
            )

async def send_alert(title: str, message: str, severity: str = "warning", metadata: Dict = None):
    """Send alert (convenience function)"""
    manager = AlertManager()
    await manager.send_alert(title, message, severity, metadata)