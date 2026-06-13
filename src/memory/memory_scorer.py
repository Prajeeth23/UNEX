import json
from src.llm.provider import LLMProvider
from src.memory.memory_models import MemoryType, MemoryRecord, ImportanceLevel

class MemoryScorer:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def extract_memories(self, user_query: str, agent_response: str) -> list[MemoryRecord]:
        prompt = f"""You are UNEX's core memory extraction module.
Analyze the following interaction and extract ANY persistent facts, user preferences, project details, or important knowledge that UNEX should remember for the future.

If there is nothing worth remembering (e.g. casual greetings), output an empty JSON array [].

Interaction:
User: {user_query}
UNEX: {agent_response}

Output ONLY valid JSON matching this schema:
[
  {{
    "type": "PreferenceMemory" | "ProjectMemory" | "TaskMemory" | "KnowledgeMemory" | "ConversationMemory",
    "content": "A clear, concise statement of the fact to remember.",
    "importance": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "tags": ["tag1", "tag2"]
  }}
]
"""
        response = await self.llm_provider.agenerate(prompt, format="json")
        
        try:
            # simple json extraction
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                records = []
                for item in data:
                    records.append(MemoryRecord(
                        type=MemoryType(item.get("type", "KnowledgeMemory")),
                        content=item["content"],
                        importance=ImportanceLevel(item.get("importance", "MEDIUM")),
                        tags=item.get("tags", [])
                    ))
                return records
        except Exception as e:
            print(f"Memory extraction parsing failed: {e}")
            
        return []
