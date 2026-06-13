import json
from src.vision.vision_models import VisionModelProvider

class ImageClassifier:
    def __init__(self, provider: VisionModelProvider):
        self.provider = provider
        
    async def classify(self, base64_img: str) -> str:
        prompt = "Classify this image into one of the following categories: 'UI', 'Document', 'Chart', 'Table', 'General'. Return only the single word category name."
        sys_prompt = "You are an image classification engine. Output only the category string."
        
        res = await self.provider.analyze_image(base64_img, prompt, sys_prompt)
        res = res.strip().title()
        
        valid = ["UI", "Document", "Chart", "Table", "General"]
        for v in valid:
            if v.lower() in res.lower():
                return v
                
        return "General"
