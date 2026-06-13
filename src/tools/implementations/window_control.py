import pygetwindow as gw
from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry

class ListWindowsTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_windows"
        
    @property
    def description(self) -> str:
        return "Lists all currently open and visible window titles."
        
    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {}, "required": []}
        
    async def execute(self, **kwargs) -> Any:
        try:
            titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
            return ToolResult.ok(data={"open_windows": titles})
        except Exception as e:
            return ToolResult.fail(str(e))

class FocusWindowTool(BaseTool):
    @property
    def name(self) -> str:
        return "focus_window"
        
    @property
    def description(self) -> str:
        return "Brings a specific window to the foreground by its title."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "title_keyword": {"type": "string", "description": "Keyword matching the window title."}
            },
            "required": ["title_keyword"]
        }
        
    async def execute(self, title_keyword: str, **kwargs) -> Any:
        try:
            windows = gw.getWindowsWithTitle(title_keyword)
            if not windows:
                return ToolResult.fail(f"No window found matching '{title_keyword}'.")
            
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            return ToolResult.ok(data={"message": f"Focused window: {win.title}"})
        except Exception as e:
            return ToolResult.fail(str(e))

class WindowStateTool(BaseTool):
    @property
    def name(self) -> str:
        return "set_window_state"
        
    @property
    def description(self) -> str:
        return "Minimizes, maximizes, or restores a window."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "title_keyword": {"type": "string", "description": "Keyword matching the window title."},
                "state": {"type": "string", "enum": ["minimize", "maximize", "restore"]}
            },
            "required": ["title_keyword", "state"]
        }
        
    async def execute(self, title_keyword: str, state: str, **kwargs) -> Any:
        try:
            windows = gw.getWindowsWithTitle(title_keyword)
            if not windows:
                return ToolResult.fail(f"No window found matching '{title_keyword}'.")
                
            win = windows[0]
            if state == "minimize":
                win.minimize()
            elif state == "maximize":
                win.maximize()
            elif state == "restore":
                win.restore()
                
            return ToolResult.ok(data={"message": f"Window '{win.title}' set to {state}."})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register
registry.register(ListWindowsTool())
registry.register(FocusWindowTool())
registry.register(WindowStateTool())
