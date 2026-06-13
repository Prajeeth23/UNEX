import os
import subprocess
from src.config.settings import settings

class RecoveryManager:
    @staticmethod
    def attempt_ollama_recovery() -> bool:
        print("[Recovery] Attempting to restart Ollama service...")
        try:
            # We assume Ollama is in PATH on Windows
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
        except Exception as e:
            print(f"[Recovery] Failed to start Ollama: {e}")
            return False
            
    @staticmethod
    def attempt_database_recovery() -> bool:
        print("[Recovery] Attempting database recovery...")
        # If unex.db is missing, we re-run alembic
        try:
            subprocess.run(["alembic", "upgrade", "head"], check=True, cwd=os.path.join(os.path.dirname(__file__), "..", ".."))
            return True
        except Exception as e:
            print(f"[Recovery] Failed to recover database: {e}")
            return False
