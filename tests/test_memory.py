import pytest
import asyncio
from src.memory.memory_manager import MemoryManager
from src.memory.memory_models import MemoryRecord, MemoryType, ImportanceLevel

# Mock LLMProvider to avoid hitting real Ollama
class MockLLMProvider:
    async def agenerate(self, prompt, **kwargs):
        return "[]"
    async def agenerate_chat(self, messages, **kwargs):
        return "mock"
    def generate(self, prompt, **kwargs):
        return "[]"
    def generate_chat(self, messages, **kwargs):
        return "mock"

@pytest.fixture
def memory_manager(tmp_path):
    db_path = str(tmp_path / "test_unex.db")
    manager = MemoryManager(MockLLMProvider(), db_path=db_path)
    yield manager
    manager.close()

def test_preference_memory(memory_manager):
    # User: "I prefer answers in Tanglish."
    pref = MemoryRecord(
        type=MemoryType.PREFERENCE,
        content="User prefers answers in Tanglish.",
        importance=ImportanceLevel.HIGH
    )
    mem_id = memory_manager.store_memory(pref)
    assert mem_id is not None
    
    # Retrieval
    results = memory_manager.search_memory("Tanglish", top_k=1)
    assert len(results) > 0
    assert results[0][0].content == "User prefers answers in Tanglish."
    
    # Verify context injection
    context = memory_manager.get_context_for_query("How should you answer this?")
    assert "Tanglish" in context or "Tanglish" in memory_manager.get_context_for_query("What language should you use?")

def test_project_memory(memory_manager):
    # User: "I am building UNEX."
    proj = MemoryRecord(
        type=MemoryType.PROJECT,
        content="User is building an AI OS named UNEX.",
        importance=ImportanceLevel.CRITICAL
    )
    memory_manager.store_memory(proj)
    
    # Search returns project
    results = memory_manager.search_memory("What am I building?", top_k=1)
    assert len(results) > 0
    assert "UNEX" in results[0][0].content

def test_forget_function(memory_manager):
    proj = MemoryRecord(
        type=MemoryType.PROJECT,
        content="User is building UNEX.",
        importance=ImportanceLevel.CRITICAL
    )
    mem_id = memory_manager.store_memory(proj)
    
    # Ensure it's there
    assert len(memory_manager.search_memory("UNEX")) > 0
    
    # Forget
    memory_manager.delete_memory(mem_id)
    
    # Ensure it's gone
    results = memory_manager.search_memory("UNEX")
    # Due to sentence-transformers returning everything but with low scores, we check for presence > 0.3
    assert len(results) == 0

def test_multi_day_persistence(memory_manager):
    # This is simulated by the fact that we can store a memory, recreate the MemoryManager on the same DB,
    # and retrieve it.
    mem = MemoryRecord(type=MemoryType.KNOWLEDGE, content="The sky is blue.", importance=ImportanceLevel.LOW)
    mem_id = memory_manager.store_memory(mem)
    db_path = str(memory_manager.SessionLocal.kw['bind'].url.database)
    
    # Recreate manager simulating restart
    new_manager = MemoryManager(MockLLMProvider(), db_path=db_path)
    try:
        memories = new_manager.store.get_all_memories()
        assert len(memories) > 0
        
        # Embeddings reload test
        results = new_manager.search_memory("sky color")
        assert len(results) > 0
        assert "blue" in results[0][0].content
    finally:
        new_manager.close()
