import aiohttp
import os
import psutil
from src.config.settings import settings

class HealthCheck:
    @staticmethod
    async def check_ollama() -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.ollama_host) as resp:
                    return resp.status == 200
        except Exception:
            return False
            
    @staticmethod
    def check_database() -> bool:
        return os.path.exists(settings.db_path)
        
    @staticmethod
    def get_system_metrics() -> dict:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_used_mb": psutil.virtual_memory().used / (1024 * 1024),
            "ram_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "disk_free_gb": psutil.disk_usage('/').free / (1024**3)
        }
