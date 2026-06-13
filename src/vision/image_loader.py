import base64
from io import BytesIO
from PIL import Image
import os

class ImageLoader:
    @staticmethod
    def load_base64_from_file(file_path: str, max_size=(1024, 1024)) -> str:
        """Loads an image from disk, resizes if too large, and returns base64."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found: {file_path}")
            
        with Image.open(file_path) as img:
            return ImageLoader._process_image(img, max_size)
            
    @staticmethod
    def load_base64_from_pil(img: Image.Image, max_size=(1024, 1024)) -> str:
        """Takes a PIL Image, resizes, and returns base64."""
        return ImageLoader._process_image(img, max_size)
        
    @staticmethod
    def _process_image(img: Image.Image, max_size=(1024, 1024)) -> str:
        # Convert to RGB if necessary (e.g. RGBA screenshots)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Resize if it exceeds max bounds to save VRAM
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        buffered = BytesIO()
        # Save as JPEG for compression before sending to LLM
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
