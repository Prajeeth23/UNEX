import psutil
import subprocess
import os
from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.tools.application_catalog import ApplicationCatalog

catalog = ApplicationCatalog()

class OpenApplicationTool(BaseTool):
    @property
    def name(self) -> str:
        return "open_application"
        
    @property
    def description(self) -> str:
        return "Opens an application by its alias (e.g., 'chrome', 'vscode', 'notepad')."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "The name or alias of the application to open."}
            },
            "required": ["app_name"]
        }
        
    async def execute(self, app_name: str, **kwargs) -> Any:
        try:
            app_path = catalog.find_app(app_name)
            if not app_path:
                return ToolResult.fail(f"Could not find application matching '{app_name}'.")
                
            # Launch in background
            os.startfile(app_path)
            return ToolResult.ok(data={"message": f"Successfully launched {app_name}."})
        except Exception as e:
            return ToolResult.fail(str(e))

class CloseApplicationTool(BaseTool):
    @property
    def name(self) -> str:
        return "close_application"
        
    @property
    def description(self) -> str:
        return "Closes a running application forcefully by matching its name."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "process_name": {"type": "string", "description": "The name of the process to kill (e.g. 'chrome.exe', 'notepad')."}
            },
            "required": ["process_name"]
        }
        
    async def execute(self, process_name: str, **kwargs) -> Any:
        killed_count = 0
        proc_name_lower = process_name.lower().replace(".exe", "")
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc_name_lower in proc.info['name'].lower():
                    proc.kill()
                    killed_count += 1
                    
            if killed_count > 0:
                return ToolResult.ok(data={"message": f"Killed {killed_count} instances of {process_name}."})
            return ToolResult.fail(f"No running processes found matching '{process_name}'.")
        except Exception as e:
            return ToolResult.fail(str(e))

class CheckRunningProcessesTool(BaseTool):
    @property
    def name(self) -> str:
        return "check_running_processes"
        
    @property
    def description(self) -> str:
        return "Returns a list of actively running top-level applications/processes."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
        
    async def execute(self, **kwargs) -> Any:
        try:
            processes = set()
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name')
                if name and name.endswith('.exe'):
                    processes.add(name)
            
            # Return top 20 to save context length
            return ToolResult.ok(data={"running_processes": list(processes)[:20]})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register tools
registry.register(OpenApplicationTool())
registry.register(CloseApplicationTool())
registry.register(CheckRunningProcessesTool())
