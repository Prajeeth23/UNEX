from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class BaseTool(ABC):
    """Abstract base class for all UNEX tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does and when to use it."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict:
        """JSON schema defining the expected arguments for the tool."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the tool with the provided arguments.
        Should return a ToolResult or dict.
        """
        pass
