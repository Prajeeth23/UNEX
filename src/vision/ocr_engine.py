import numpy as np
from PIL import Image

class OCREngine:
    def __init__(self):
        self._engine = None
        self._engine_type = None
            
    @property
    def engine(self):
        if self._engine is None:
            # 1. Try RapidOCR (PP-OCRv4 on ONNX Runtime - fast, reliable, no DLL conflict)
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._engine = RapidOCR()
                self._engine_type = "rapidocr"
                return self._engine
            except Exception as e_rapid:
                pass

            # 2. Try PaddleOCR fallback
            try:
                import torch # Mitigate Windows DLL conflict
                from paddleocr import PaddleOCR
                self._engine = PaddleOCR(use_angle_cls=True, lang='en')
                self._engine_type = "paddleocr"
            except Exception as e:
                print(f"[OCREngine] OCR engines unavailable ({e}). OCR disabled.")
                self._engine = False
        return self._engine if self._engine is not False else None
            
    def extract_text(self, img: Image.Image) -> str:
        if not self.engine:
            return ""
            
        # Convert PIL to numpy array
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_np = np.array(img)
        
        text_lines = []
        try:
            if self._engine_type == "rapidocr":
                result, _ = self.engine(img_np)
                if result:
                    for line in result:
                        text_lines.append(line[1])
            elif self._engine_type == "paddleocr":
                result = self.engine.ocr(img_np, cls=True)
                if result and result[0]:
                    for line in result[0]:
                        text_lines.append(line[1][0])
        except Exception as e:
            print(f"[OCREngine] Error during text extraction: {e}")
            return ""
                
        return "\n".join(text_lines)
