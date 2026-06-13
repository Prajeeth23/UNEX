from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.rag.rag_manager import RAGManager

_rag_manager = None
def get_rag_manager() -> RAGManager:
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = RAGManager()
    return _rag_manager

class IndexDocumentTool(BaseTool):
    @property
    def name(self) -> str:
        return "index_document"
        
    @property
    def description(self) -> str:
        return "Reads a local text file and indexes it into the UNEX personal knowledge base (Qdrant)."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the document."}
            },
            "required": ["filepath"]
        }
        
    async def execute(self, filepath: str, **kwargs) -> Any:
        try:
            await get_rag_manager().index_file(filepath)
            return ToolResult.ok(data={"status": "Success", "file": filepath})
        except Exception as e:
            return ToolResult.fail(str(e))

class SearchKnowledgeTool(BaseTool):
    @property
    def name(self) -> str:
        return "search_knowledge"
        
    @property
    def description(self) -> str:
        return "Performs semantic search on the UNEX personal knowledge base."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search question or concept."}
            },
            "required": ["query"]
        }
        
    async def execute(self, query: str, **kwargs) -> Any:
        try:
            results = await get_rag_manager().search(query)
            return ToolResult.ok(data={"query": query, "results": results})
        except Exception as e:
            return ToolResult.fail(str(e))

registry.register(IndexDocumentTool())
registry.register(SearchKnowledgeTool())
