"""
Health Check Module - Simplified (No psutil)
"""

from typing import Dict, Any
from datetime import datetime
import asyncio

from app.core.deepseek import deepseek_client
from app.database.session import check_db_connection
from app.core.cache import check_redis_connection
from app.config import config
from app.utils.logger import logger


class HealthChecker:
    """System health checker - Simplified"""
    
    async def check_all(self) -> Dict[str, Any]:
        """Check all system components"""
        results = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_deepseek(),
            return_exceptions=True
        )
        
        checks = {
            "database": results[0] if not isinstance(results[0], Exception) else {"healthy": False, "error": str(results[0])},
            "redis": results[1] if not isinstance(results[1], Exception) else {"healthy": False, "error": str(results[1])},
            "deepseek": results[2] if not isinstance(results[2], Exception) else {"healthy": False, "error": str(results[2])}
        }
        
        all_healthy = all(check.get("healthy", False) for check in checks.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            return await check_db_connection()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            return await check_redis_connection()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_deepseek(self) -> Dict[str, Any]:
        """Check DeepSeek API health"""
        try:
            return await deepseek_client.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}


# Global instance
health_checker = HealthChecker()


async def get_system_health() -> Dict[str, Any]:
    """Get system health"""
    return await health_checker.check_all()


async def check_disk_space() -> Dict[str, Any]:
    """Check disk space - simplified"""
    return {
        "healthy": True,
        "message": "Disk check skipped (psutil not available)"
    }


async def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage - simplified"""
    return {
        "healthy": True,
        "message": "Memory check skipped (psutil not available)"
    }