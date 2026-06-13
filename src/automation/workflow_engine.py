from src.automation.scheduler import SchedulerManager
from src.automation.folder_monitor import FolderMonitor
import asyncio

class WorkflowEngine:
    def __init__(self):
        self.scheduler = SchedulerManager()
        self.folder_monitor = FolderMonitor()
        
    def schedule_agent_task(self, prompt: str, interval_minutes: int):
        """Schedules a recurring task that the agent will execute."""
        def task_runner():
            # In a full implementation, this pushes the prompt to the UNEXAgent's message queue
            print(f"\n[WorkflowEngine] Executing scheduled agent task: '{prompt}'")
            
        job_id = self.scheduler.schedule_task(task_runner, 'interval', minutes=interval_minutes)
        return job_id
        
    def monitor_and_index(self, folder_path: str):
        """Monitors a folder and automatically indexes new documents into RAG."""
        def on_new_file(filepath):
            from src.rag.rag_manager import RAGManager
            rag = RAGManager()
            print(f"[WorkflowEngine] Auto-indexing new file: {filepath}")
            # We run it in the event loop if possible, or use asyncio.run
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(rag.index_file(filepath))
            except RuntimeError:
                asyncio.run(rag.index_file(filepath))
                
        return self.folder_monitor.watch_folder(folder_path, on_new_file)
