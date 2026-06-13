import os
import time
from PIL import Image

class ScreenshotManager:
    def __init__(self):
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "visual_memory"))
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def save_screenshot(self, img: Image.Image) -> str:
        """Saves screenshot as compressed WEBP and returns the path."""
        timestamp = int(time.time())
        filename = f"screen_{timestamp}.webp"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Save compressed
        img.save(filepath, format="WEBP", quality=50)
        
        # We can implement a rolling delete here (e.g. keep last 100)
        self._cleanup_old_screenshots()
        
        return filepath
        
    def _cleanup_old_screenshots(self, max_files=100):
        try:
            files = [os.path.join(self.storage_dir, f) for f in os.listdir(self.storage_dir) if f.endswith(".webp")]
            if len(files) > max_files:
                files.sort(key=os.path.getctime)
                files_to_delete = files[:-max_files]
                for f in files_to_delete:
                    os.remove(f)
        except Exception as e:
            print(f"[ScreenshotManager] Cleanup error: {e}")
