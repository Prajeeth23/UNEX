import os
import glob
from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry

class DirectoryListingTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_directory"
        
    @property
    def description(self) -> str:
        return "Lists the contents of a specified directory."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the directory."}
            },
            "required": ["path"]
        }
        
    async def execute(self, path: str, **kwargs) -> Any:
        try:
            if not os.path.exists(path):
                return ToolResult.fail(f"Path does not exist: {path}")
            if not os.path.isdir(path):
                return ToolResult.fail(f"Path is not a directory: {path}")
                
            items = os.listdir(path)
            result = []
            for item in items:
                full_path = os.path.join(path, item)
                result.append({
                    "name": item,
                    "is_dir": os.path.isdir(full_path),
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                })
            return ToolResult.ok(data=result)
        except Exception as e:
            return ToolResult.fail(str(e))

class FileReadTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"
        
    @property
    def description(self) -> str:
        return "Reads the text contents of a file."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the file."}
            },
            "required": ["path"]
        }
        
    async def execute(self, path: str, **kwargs) -> Any:
        try:
            if not os.path.exists(path):
                return ToolResult.fail(f"File does not exist: {path}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult.ok(data={"content": content})
        except Exception as e:
            return ToolResult.fail(str(e))

class FileWriteTool(BaseTool):
    @property
    def name(self) -> str:
        return "write_file"
        
    @property
    def description(self) -> str:
        return "Writes text content to a file, overwriting it if it exists."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the file."},
                "content": {"type": "string", "description": "The text content to write."}
            },
            "required": ["path", "content"]
        }
        
    async def execute(self, path: str, content: str, **kwargs) -> Any:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult.ok(data={"message": f"Successfully wrote to {path}"})
        except Exception as e:
            return ToolResult.fail(str(e))

class FileSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "search_files"
        
    @property
    def description(self) -> str:
        return "Searches for files matching a pattern (e.g. *.txt) in a directory recursively."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "The directory to start searching from."},
                "pattern": {"type": "string", "description": "The glob pattern to search for, e.g. '*.py' or '*log*'"}
            },
            "required": ["directory", "pattern"]
        }
        
    async def execute(self, directory: str, pattern: str, **kwargs) -> Any:
        try:
            if not os.path.exists(directory):
                return ToolResult.fail(f"Directory does not exist: {directory}")
                
            search_path = os.path.join(directory, "**", pattern)
            matches = glob.glob(search_path, recursive=True)
            return ToolResult.ok(data={"matches": matches})
        except Exception as e:
            return ToolResult.fail(str(e))

# Register tools
registry.register(DirectoryListingTool())
registry.register(FileReadTool())
registry.register(FileWriteTool())
registry.register(FileSearchTool())
