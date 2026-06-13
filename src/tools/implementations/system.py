import os
import subprocess
import platform
import psutil
import GPUtil
from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry

class SystemInformationTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_system_info"
        
    @property
    def description(self) -> str:
        return "Retrieves information about the operating system, CPU, memory, and disk."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
        
    async def execute(self, **kwargs) -> Any:
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            
            gpu_info = []
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info.append({
                        "name": gpu.name,
                        "load": f"{gpu.load * 100:.1f}%",
                        "memory_total": f"{gpu.memoryTotal}MB",
                        "memory_used": f"{gpu.memoryUsed}MB"
                    })
            except Exception:
                pass

            info = {
                "os": platform.system(),
                "cpu_usage": f"{psutil.cpu_percent(interval=0.5)}%",
                "ram_usage": f"{mem.percent}%",
                "ram_available_gb": round(mem.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "network_bytes_sent": net.bytes_sent,
                "network_bytes_recv": net.bytes_recv,
                "gpus": gpu_info
            }
            return ToolResult.ok(data=info)
        except Exception as e:
            return ToolResult.fail(str(e))

class ApplicationLaunchTool(BaseTool):
    @property
    def name(self) -> str:
        return "launch_application"
        
    @property
    def description(self) -> str:
        return "Launches an application or executable file on the host machine."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command or path to the application to run."}
            },
            "required": ["command"]
        }
        
    async def execute(self, command: str, **kwargs) -> Any:
        try:
            # Running asynchronously in the background so UNEX doesn't block
            subprocess.Popen(command, shell=True)
            return ToolResult.ok(data={"message": f"Launched '{command}' successfully."})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register tools
registry.register(SystemInformationTool())
registry.register(ApplicationLaunchTool())
