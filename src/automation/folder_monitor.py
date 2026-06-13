import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WorkflowEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            print(f"[FolderMonitor] Detected new file: {event.src_path}")
            self.callback(event.src_path)

class FolderMonitor:
    def __init__(self):
        self.observers = {}
        
    def watch_folder(self, folder_path: str, callback) -> str:
        """Starts monitoring a folder and calls callback(filepath) on new files."""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
            
        event_handler = WorkflowEventHandler(callback)
        observer = Observer()
        observer.schedule(event_handler, path=folder_path, recursive=False)
        observer.start()
        
        watch_id = folder_path
        self.observers[watch_id] = observer
        print(f"[FolderMonitor] Started watching: {folder_path}")
        return watch_id
        
    def stop_watching(self, watch_id: str):
        if watch_id in self.observers:
            observer = self.observers.pop(watch_id)
            observer.stop()
            observer.join()
            print(f"[FolderMonitor] Stopped watching: {watch_id}")
