from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.automation.workflow_engine import WorkflowEngine

workflow = WorkflowEngine()

class ScheduleTaskTool(BaseTool):
    @property
    def name(self) -> str:
        return "schedule_task"
        
    @property
    def description(self) -> str:
        return "Schedules a recurring background prompt for the UNEX Agent (e.g., run every 60 minutes)."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The command or prompt to execute."},
                "interval_minutes": {"type": "integer", "description": "Minutes between executions."}
            },
            "required": ["prompt", "interval_minutes"]
        }
        
    async def execute(self, prompt: str, interval_minutes: int, **kwargs) -> Any:
        try:
            job_id = workflow.schedule_agent_task(prompt, interval_minutes)
            return ToolResult.ok(data={"status": "Scheduled", "job_id": job_id})
        except Exception as e:
            return ToolResult.fail(str(e))

class WatchFolderTool(BaseTool):
    @property
    def name(self) -> str:
        return "watch_folder"
        
    @property
    def description(self) -> str:
        return "Starts monitoring a specific folder. Any new files dropped in will be automatically indexed into the RAG Knowledge Base."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Absolute path to monitor."}
            },
            "required": ["folder_path"]
        }
        
    async def execute(self, folder_path: str, **kwargs) -> Any:
        try:
            watch_id = workflow.monitor_and_index(folder_path)
            return ToolResult.ok(data={"status": "Watching", "watch_id": watch_id})
        except Exception as e:
            return ToolResult.fail(str(e))

registry.register(ScheduleTaskTool())
registry.register(WatchFolderTool())
