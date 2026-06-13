from pydantic import BaseModel
from typing import Any, Optional

class ToolResult(BaseModel):
    """Standardized output for tool execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, data: Any = None):
        return cls(success=True, data=data)
        
    @classmethod
    def fail(cls, error: str):
        return cls(success=False, error=error)
