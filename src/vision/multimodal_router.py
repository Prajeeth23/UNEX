from src.vision.vision_models import VisionModelProvider
from src.vision.image_classifier import ImageClassifier
from src.vision.ui_detector import UIDetector
from src.vision.document_analyzer import DocumentAnalyzer
from src.vision.chart_analyzer import ChartAnalyzer
from src.vision.table_extractor import TableExtractor
from typing import Dict, Any

class MultimodalRouter:
    """Routes an image to the specialized Vision prompt/model based on classification."""
    
    def __init__(self, provider: VisionModelProvider):
        self.classifier = ImageClassifier(provider)
        self.ui_detector = UIDetector(provider)
        self.doc_analyzer = DocumentAnalyzer(provider)
        self.chart_analyzer = ChartAnalyzer(provider)
        self.table_extractor = TableExtractor(provider)
        
    async def process_image(self, base64_img: str, explicit_type: str = None) -> Dict[str, Any]:
        img_type = explicit_type or await self.classifier.classify(base64_img)
        print(f"[MultimodalRouter] Processing as: {img_type}")
        
        result = {"classification": img_type}
        
        if img_type == "UI":
            result["analysis"] = await self.ui_detector.analyze(base64_img)
        elif img_type == "Document":
            result["analysis"] = await self.doc_analyzer.analyze(base64_img)
        elif img_type == "Chart":
            result["analysis"] = await self.chart_analyzer.analyze(base64_img)
        elif img_type == "Table":
            result["analysis"] = {"rows": await self.table_extractor.extract(base64_img)}
        else:
            # General fallback
            prompt = "Describe what you see in this image in detail."
            result["analysis"] = {"description": await self.classifier.provider.analyze_image(base64_img, prompt)}
            
        return result
