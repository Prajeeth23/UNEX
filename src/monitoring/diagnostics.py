from src.monitoring.metrics import SystemMetrics
from src.startup.healthcheck import HealthCheck

class DiagnosticsEngine:
    @staticmethod
    async def run_full_diagnostics() -> dict:
        ollama_status = await HealthCheck.check_ollama()
        db_status = HealthCheck.check_database()
        metrics = SystemMetrics.get_snapshot()
        
        status = "Healthy"
        if not ollama_status or not db_status:
            status = "Degraded"
        if metrics["memory"]["percent"] > 90:
            status = "Warning: High RAM"
            
        return {
            "status": status,
            "components": {
                "ollama": "Online" if ollama_status else "Offline",
                "database": "Online" if db_status else "Missing"
            },
            "metrics": metrics
        }
