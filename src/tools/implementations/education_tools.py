from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.education.education_manager import EducationManager
from src.education.paper_analyzer import PaperAnalyzer

edu_manager = EducationManager()

class AnalyzeQuestionPaperTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_question_paper"
        
    @property
    def description(self) -> str:
        return "Analyzes an educational PDF (Question Paper) and returns statistics like total marks, question types, and metadata."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "pdf_path": {"type": "string", "description": "Absolute path to the PDF file."}
            },
            "required": ["pdf_path"]
        }
        
    async def execute(self, pdf_path: str, **kwargs) -> Any:
        try:
            json_data = await edu_manager.process_pdf(pdf_path)
            analysis = PaperAnalyzer.analyze(json_data)
            return ToolResult.ok(data=analysis)
        except Exception as e:
            return ToolResult.fail(str(e))

class ConvertPdfToJsonTool(BaseTool):
    @property
    def name(self) -> str:
        return "convert_pdf_to_json"
        
    @property
    def description(self) -> str:
        return "Converts an academic PDF into a structured Educational JSON schema."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "pdf_path": {"type": "string", "description": "Absolute path to the PDF file."}
            },
            "required": ["pdf_path"]
        }
        
    async def execute(self, pdf_path: str, **kwargs) -> Any:
        try:
            json_data = await edu_manager.process_pdf(pdf_path)
            # Dump to string but return as raw dict for the LLM context
            return ToolResult.ok(data={"questions_extracted": len(json_data.questions), "status": "Success"})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register Tools
registry.register(AnalyzeQuestionPaperTool())
registry.register(ConvertPdfToJsonTool())
