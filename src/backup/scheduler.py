from src.automation.scheduler import SchedulerManager
from src.backup.exporter import BackupExporter

class BackupScheduler:
    def __init__(self, scheduler_manager: SchedulerManager):
        self.scheduler = scheduler_manager
        
    def schedule_daily_backup(self):
        """Schedules a backup to run every 24 hours."""
        def run_backup():
            try:
                BackupExporter.create_backup()
            except Exception as e:
                print(f"[BackupScheduler] Scheduled backup failed: {e}")
                
        self.scheduler.schedule_task(run_backup, 'interval', hours=24)
        print("[BackupScheduler] Daily backups enabled.")
