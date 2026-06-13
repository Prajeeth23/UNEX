import pytest
import os
import asyncio
from src.rag.vector_store import VectorStore
from src.automation.scheduler import SchedulerManager

def test_vector_store_initialization():
    store = VectorStore(collection_name="test_collection")
    assert store is not None
    # Assuming Qdrant local setup passes
    
def test_scheduler_manager():
    manager = SchedulerManager()
    
    def dummy_task():
        pass
        
    job_id = manager.schedule_task(dummy_task, 'interval', seconds=1)
    assert job_id is not None
    manager.cancel_task(job_id)
