from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response based on the prompt."""
        pass

    @abstractmethod
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a list of chat messages."""
        pass

    @abstractmethod
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Generate a response asynchronously."""
        pass
