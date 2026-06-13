import asyncio
from src.startup.healthcheck import HealthCheck
from src.startup.recovery import RecoveryManager
from src.config.settings import settings

async def bootstrap_unex() -> bool:
    print("[Bootstrap] Initializing UNEX System Checks...")
    
    # 1. Check Database
    db_ok = HealthCheck.check_database()
    if not db_ok:
        print("[Bootstrap] Database missing. Attempting recovery...")
        recovered = RecoveryManager.attempt_database_recovery()
        if not recovered:
            settings.enable_safe_mode()
            return False
            
    # 2. Check Ollama
    ollama_ok = await HealthCheck.check_ollama()
    if not ollama_ok:
        print("[Bootstrap] Ollama unreachable. Attempting to start service...")
        started = RecoveryManager.attempt_ollama_recovery()
        if started:
            # Wait a few seconds for it to bind
            await asyncio.sleep(5)
            ollama_ok = await HealthCheck.check_ollama()
            
        if not ollama_ok:
            print("[Bootstrap] CRITICAL: Ollama failed to start.")
            settings.enable_safe_mode()
            return False
            
    print("[Bootstrap] All systems nominal. Starting in Production Mode.")
    return True
    
if __name__ == "__main__":
    asyncio.run(bootstrap_unex())
