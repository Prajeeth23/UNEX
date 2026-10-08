import numpy as np
from PIL import Image

class OCREngine:
    def __init__(self):
        self._engine = None
            
    @property
    def engine(self):
        if self._engine is None:
            try:
                from paddleocr import PaddleOCR
                self._engine = PaddleOCR(use_angle_cls=True, lang='en')
            except Exception as e:
                print(f"[OCREngine] PaddleOCR unavailable ({e}). OCR disabled.")
                self._engine = False
        return self._engine if self._engine is not False else None
            
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
