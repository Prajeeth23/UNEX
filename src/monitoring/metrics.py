import psutil
import threading
from src.config.settings import settings

class SystemMetrics:
    @staticmethod
    def get_snapshot() -> dict:
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.1),
                "cores": psutil.cpu_count(logical=True)
            },
            "memory": {
                "total_mb": round(psutil.virtual_memory().total / (1024 * 1024), 2),
                "used_mb": round(psutil.virtual_memory().used / (1024 * 1024), 2),
                "percent": psutil.virtual_memory().percent
            },
            "process": {
                "threads": threading.active_count(),
                "active_llm": settings.llm_model,
                "active_vision": settings.vision_model,
                "profile": settings.profile.value
            }
        }
