import fitz  # PyMuPDF
import os
import numpy as np

class PDFParser:
    def __init__(self, use_ocr: bool = True):
        self.use_ocr = use_ocr
        self._ocr_engine = None

    @property
    def ocr_engine(self):
        if self._ocr_engine is None and self.use_ocr:
            try:
                from paddleocr import PaddleOCR
                self._ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')
            except Exception as e:
                print(f"[PDFParser] PaddleOCR unavailable ({e}). Falling back to digital-only extraction.")
                self.use_ocr = False
                self._ocr_engine = None
        return self._ocr_engine

    def extract_text(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        full_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            
            # If the page has almost no text, it might be a scanned image
            if len(text) < 50 and self.ocr_engine:
                print(f"[PDFParser] Page {page_num+1} appears to be a scan. Running OCR...")
                ocr_text = self._extract_ocr(page)
                full_text.append(ocr_text)
            else:
                full_text.append(text)
                
        doc.close()
        return "\n\n".join(full_text)
        
    def _extract_ocr(self, page: fitz.Page) -> str:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Scale 2x for better OCR
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # If it's RGBA, convert to RGB
        if pix.n == 4:
            import cv2
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
        result = self.ocr_engine.ocr(img_np, cls=True)
        
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                # line format: [[bbox], (text, confidence)]
                text_lines.append(line[1][0])
                
        return "\n".join(text_lines)
