import os
import time
import uuid
from pathlib import Path
import psutil

# Add project root to sys path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory.memory_manager import MemoryManager
from src.memory.memory_models import MemoryRecord, MemoryType, ImportanceLevel

# Dummy LLM Provider
class MockLLMProvider:
    def agenerate(self, *args, **kwargs): pass
    def agenerate_chat(self, *args, **kwargs): pass
    def generate(self, *args, **kwargs): pass
    def generate_chat(self, *args, **kwargs): pass

def run_benchmark():
    db_path = "database/benchmark_unex.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Initializing Memory Manager for Benchmark...")
    manager = MemoryManager(MockLLMProvider(), db_path=db_path)
    
    volumes = [1000, 5000, 10000]
    
    # Sentence-transformers generates identical embeddings for identical text.
    # To simulate real usage, we just embed a few different strings to avoid overhead of 10000 unique embeddings 
    # taking hours during the benchmark script execution, BUT wait, the database size and memory usage
    # need to be accurate. We will use a unique string for each memory.
    # To speed up insertion, we can pre-calculate a dummy embedding (length 384 for all-MiniLM)
    # but the retriever explicitly encodes the content. Let's just generate it since the model is fast.
    
    print(f"\nTarget Hardware Constraints:")
    print("- Ryzen 7 7445HS")
    print("- 16 GB RAM")
    print("- Retrieval < 500ms")
    print("-" * 40)
    
    total_memories = 0
    for target_volume in volumes:
        to_insert = target_volume - total_memories
        print(f"\nInserting {to_insert} memories to reach {target_volume}...")
        
        # Batch insert simulation
        start_time = time.time()
        for i in range(to_insert):
            # Using pre-calculated embeddings for the benchmark to simulate the DATABASE scale and search scale
            # without taking 30 minutes to run sentence-transformers on 10k items during this test.
            # We bypass the manager's store_memory and use store directly for speed in setup.
            # But the search will test the full retrieval pipeline.
            mem = MemoryRecord(
                id=str(uuid.uuid4()),
                type=MemoryType.KNOWLEDGE,
                content=f"This is a benchmark memory record number {total_memories + i}",
                importance=ImportanceLevel.LOW
            )
            dummy_embedding = [0.01] * 384
            manager.store.store_memory(mem, dummy_embedding)
        
        total_memories = target_volume
        insert_time = time.time() - start_time
        print(f"Insertion complete in {insert_time:.2f}s")
        
        # Test Retrieval
        # Force re-loading of embeddings to simulate real search memory usage
        # The retriever caches nothing, it loads from DB on every search right now.
        start_search = time.time()
        results = manager.search_memory("benchmark test query")
        search_time = time.time() - start_search
        
        # Measure DB Size
        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
        
        # Measure RAM usage
        process = psutil.Process(os.getpid())
        ram_mb = process.memory_info().rss / (1024 * 1024)
        
        print(f"--- Benchmark Results for {target_volume} Memories ---")
        print(f"Retrieval Latency: {search_time * 1000:.2f} ms")
        print(f"Database Size:     {db_size_mb:.2f} MB")
        print(f"Process RAM Usage: {ram_mb:.2f} MB")
        print(f"Passes constraint? {'YES' if search_time < 0.5 else 'NO'}")

    # Cleanup
    try:
        manager.store.SessionLocal.kw['bind'].dispose()
    except Exception:
        pass
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

if __name__ == "__main__":
    run_benchmark()

