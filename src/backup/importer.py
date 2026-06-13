import os
import zipfile
from src.config.settings import settings

class BackupImporter:
    @staticmethod
    def restore_backup(zip_path: str) -> bool:
        if not os.path.exists(zip_path):
            print(f"[BackupImporter] Backup file not found: {zip_path}")
            return False
            
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(root_dir)
            print("[BackupImporter] Successfully restored backup.")
            return True
        except Exception as e:
            print(f"[BackupImporter] Restoration failed: {e}")
            return False
