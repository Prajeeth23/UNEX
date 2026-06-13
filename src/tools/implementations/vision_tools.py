from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.vision.vision_manager import VisionManager

vision_manager = VisionManager()

class AnalyzeScreenTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_screen"
        
    @property
    def description(self) -> str:
        return "Captures and analyzes the current screen. Pass 'fullscreen' or 'active' for the region."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "region": {"type": "string", "enum": ["fullscreen", "active"], "description": "Which part of the screen to capture."}
            },
            "required": []
        }
        
    async def execute(self, region: str = "fullscreen", **kwargs) -> Any:
        try:
            result = await vision_manager.analyze_screen(region)
            return ToolResult.ok(data=result)
        except Exception as e:
            return ToolResult.fail(str(e))

class AnalyzeImageFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_image_file"
        
    @property
    def description(self) -> str:
        return "Analyzes an image file from disk (e.g. to read a chart or document)."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the image file."}
            },
            "required": ["filepath"]
        }
        
    async def execute(self, filepath: str, **kwargs) -> Any:
        try:
            result = await vision_manager.analyze_image_file(filepath)
            return ToolResult.ok(data=result)
        except Exception as e:
            return ToolResult.fail(str(e))

class ExtractScreenTextTool(BaseTool):
    @property
    def name(self) -> str:
        return "extract_screen_text"
        
    @property
    def description(self) -> str:
        return "Performs fast OCR on the current screen to read text."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
        
    async def execute(self, **kwargs) -> Any:
        try:
            text = vision_manager.extract_text_from_screen()
            return ToolResult.ok(data={"text": text})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register Tools
registry.register(AnalyzeScreenTool())
registry.register(AnalyzeImageFileTool())
registry.register(ExtractScreenTextTool())
