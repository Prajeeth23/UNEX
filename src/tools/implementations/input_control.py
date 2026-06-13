from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry

class KeyboardControlTool(BaseTool):
    @property
    def name(self) -> str:
        return "keyboard_control"
        
    @property
    def description(self) -> str:
        return "Injects keyboard keystrokes."
        
    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {"keys": {"type": "string"}}, "required": ["keys"]}
        
    async def execute(self, **kwargs) -> Any:
        return ToolResult.fail("Disabled until Milestone 6 (Safety Constraints).")

class MouseControlTool(BaseTool):
    @property
    def name(self) -> str:
        return "mouse_control"
        
    @property
    def description(self) -> str:
        return "Controls mouse movement and clicks."
        
    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": []}
        
    async def execute(self, **kwargs) -> Any:
        return ToolResult.fail("Disabled until Milestone 6 (Safety Constraints).")

class ClipboardControlTool(BaseTool):
    @property
    def name(self) -> str:
        return "clipboard_control"
        
    @property
    def description(self) -> str:
        return "Reads or writes to the system clipboard."
        
    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {"text": {"type": "string"}}, "required": []}
        
    async def execute(self, **kwargs) -> Any:
        return ToolResult.fail("Disabled until Milestone 6 (Safety Constraints).")

registry.register(KeyboardControlTool())
registry.register(MouseControlTool())
registry.register(ClipboardControlTool())
