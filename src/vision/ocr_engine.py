import numpy as np
from PIL import Image

class OCREngine:
    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            self.engine = PaddleOCR(use_angle_cls=True, lang='en')
        except ImportError:
            print("[OCREngine] PaddleOCR not found. OCR disabled.")
            self.engine = None
            
    def extract_text(self, img: Image.Image) -> str:
        if not self.engine:
            return ""
            
        # Convert PIL to numpy array
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_np = np.array(img)
        
        # BGR for OpenCV / PaddleOCR compatibility
        # img_np = img_np[:, :, ::-1].copy()
        
        result = self.engine.ocr(img_np, cls=True)
        
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                text_lines.append(line[1][0])
                
        return "\n".join(text_lines)
