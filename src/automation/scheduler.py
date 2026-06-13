import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        print("[SchedulerManager] Background scheduler started.")
        
    def schedule_task(self, func, trigger='interval', **trigger_args):
        """
        Schedules a task.
        Example: schedule_task(my_func, 'interval', minutes=10)
                 schedule_task(my_func, 'date', run_date=datetime(2026,6,12,23,0,0))
        """
        job = self.scheduler.add_job(func, trigger, **trigger_args)
        print(f"[SchedulerManager] Scheduled job {job.id} using {trigger}")
        return job.id
        
    def cancel_task(self, job_id: str):
        self.scheduler.remove_job(job_id)
        print(f"[SchedulerManager] Canceled job {job_id}")
