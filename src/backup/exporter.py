import os
import shutil
import zipfile
import time
from src.config.settings import settings

class BackupExporter:
    @staticmethod
    def create_backup() -> str:
        backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backups"))
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_zip = os.path.join(backup_dir, f"unex_backup_{timestamp}.zip")
        
        paths_to_backup = [
            settings.db_path,
            settings.knowledge_db_path,
            settings.visual_memory_path,
            settings.settings_file
        ]
        
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for path in paths_to_backup:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        for root, _, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), "..", ".."))
                                zipf.write(file_path, arcname)
                    else:
                        arcname = os.path.basename(path)
                        zipf.write(path, arcname)
                        
        print(f"[BackupExporter] Created backup: {backup_zip}")
        return backup_zip
