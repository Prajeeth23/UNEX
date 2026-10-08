from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    PREFERENCE = "PreferenceMemory"
    PROJECT = "ProjectMemory"
    TASK = "TaskMemory"
    KNOWLEDGE = "KnowledgeMemory"
    CONVERSATION = "ConversationMemory"

class ImportanceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MemoryRecord(BaseModel):
    id: Optional[str] = None
    type: MemoryType
    content: str
    importance: ImportanceLevel = Field(default=ImportanceLevel.MEDIUM)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)
