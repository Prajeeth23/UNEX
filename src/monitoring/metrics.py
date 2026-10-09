import psutil
import threading
from src.config.settings import settings
import GPUtil

class SystemMetrics:
    @staticmethod
    def get_snapshot() -> dict:
        gpu_info = []
        try:
            gpus = GPUtil.getGPUs()
            for g in gpus:
                gpu_info.append({
                    "name": g.name,
                    "load_percent": round(g.load * 100, 1),
                    "memory_used_mb": round(g.memoryUsed, 1),
                    "memory_total_mb": round(g.memoryTotal, 1),
                    "memory_percent": round((g.memoryUsed / g.memoryTotal) * 100, 1) if g.memoryTotal > 0 else 0
                })
        except Exception:
            pass

        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.05),
                "cores": psutil.cpu_count(logical=True)
            },
            "memory": {
                "total_mb": round(psutil.virtual_memory().total / (1024 * 1024), 2),
                "used_mb": round(psutil.virtual_memory().used / (1024 * 1024), 2),
                "percent": psutil.virtual_memory().percent
            },
            "gpu": gpu_info,
            "process": {
                "threads": threading.active_count(),
                "active_llm": settings.llm_model,
                "active_vision": settings.vision_model,
                "profile": settings.profile.value
            }
        }

