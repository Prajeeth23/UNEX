import asyncio
from typing import List, Tuple
from src.llm.provider import LLMProvider
from src.memory.database import init_db
from src.memory.memory_store import MemoryStore
from src.memory.memory_retriever import MemoryRetriever
from src.memory.memory_scorer import MemoryScorer
from src.memory.memory_models import MemoryRecord, MemoryType, ImportanceLevel

class MemoryManager:
    def __init__(self, llm_provider: LLMProvider, db_path: str = "database/unex.db"):
        self.SessionLocal = init_db(db_path)
        self.store = MemoryStore(self.SessionLocal)
        self.retriever = MemoryRetriever(self.store)
        self.scorer = MemoryScorer(llm_provider)

    def store_memory(self, memory: MemoryRecord) -> str:
        embedding = self.retriever.embed_text(memory.content)
        mem_id = self.store.store_memory(memory, embedding)
        self.retriever.mark_dirty()
        return mem_id

    def search_memory(self, query: str, top_k: int = 5, min_score: float = 0.2) -> List[Tuple[MemoryRecord, float]]:
        return self.retriever.search(query, top_k, min_score)

    def get_context_for_query(self, query: str) -> str:
        results = self.search_memory(query)
        if not results:
            return ""
            
        context_str = "Relevant Memories:\n"
        for mem, score in results:
            context_str += f"- [{mem.type.value}] {mem.content}\n"
            
        return context_str

    async def process_interaction(self, user_query: str, agent_response: str):
        """Asynchronously extracts and stores memories from an interaction."""
        memories = await self.scorer.extract_memories(user_query, agent_response)
        for mem in memories:
            self.store_memory(mem)
            print(f"[UNEX Memory] Extracted and stored: {mem.content}")

    def delete_memory(self, memory_id: str):
        self.store.delete_memory(memory_id)
        self.retriever.mark_dirty()

    def prune_decayed_memories(self, max_age_days: int = 30, max_capacity: int = None) -> int:
        """Prunes decayed low-importance memories and refreshes vector search index."""
        count = self.store.prune_memories(max_age_days=max_age_days, max_capacity=max_capacity)
        if count > 0:
            self.retriever.mark_dirty()
        return count


    def close(self):
        """Disposes the SQLite engine to prevent file locking on Windows."""
        try:
            bind = getattr(self.SessionLocal, 'kw', {}).get('bind')
            if bind:
                bind.dispose()
        except Exception:
            pass
        
    def execute_manual_command(self, command: str, content: str) -> str:
        """Handles explicit remember/forget commands for immediate action."""
        if command == "remember":
            mem = MemoryRecord(type=MemoryType.KNOWLEDGE, content=content, importance=ImportanceLevel.HIGH)
            self.store_memory(mem)
            return "I will remember that."
        # Forget is trickier without a specific ID, but a semantic search could find the closest and delete it
        return "Command not supported manually yet."
