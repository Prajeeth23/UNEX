from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
from datetime import datetime, timezone

from src.memory.database import MemoryDB, MemoryEmbeddingDB, MemoryAccessLogDB
from src.memory.memory_models import MemoryRecord, MemoryType, ImportanceLevel

class MemoryStore:
    def __init__(self, SessionLocal):
        self.SessionLocal = SessionLocal

    def store_memory(self, memory: MemoryRecord, embedding: Optional[list] = None) -> str:
        if not memory.id:
            memory.id = str(uuid.uuid4())

        with self.SessionLocal() as session:
            # Store memory
            db_memory = MemoryDB(
                id=memory.id,
                type=memory.type.value,
                content=memory.content,
                importance=memory.importance.value,
                created_at=memory.created_at,
                last_accessed=memory.last_accessed,
                tags=json.dumps(memory.tags)
            )
            session.add(db_memory)

            # Store embedding if provided
            if embedding:
                db_emb = MemoryEmbeddingDB(
                    memory_id=memory.id,
                    embedding_vector=json.dumps(embedding)
                )
                session.add(db_emb)

            session.commit()
            return memory.id

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        with self.SessionLocal() as session:
            db_mem = session.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
            if db_mem:
                self._log_access(session, memory_id)
                session.commit()
                return self._to_pydantic(db_mem)
        return None
        
    def get_all_memories(self, memory_type: Optional[MemoryType] = None) -> List[MemoryRecord]:
        with self.SessionLocal() as session:
            query = session.query(MemoryDB)
            if memory_type:
                query = query.filter(MemoryDB.type == memory_type.value)
            results = query.all()
            return [self._to_pydantic(m) for m in results]
            
    def get_all_embeddings(self) -> dict:
        """Returns a mapping of memory_id -> embedding (list of floats)"""
        with self.SessionLocal() as session:
            results = session.query(MemoryEmbeddingDB).all()
            return {r.memory_id: json.loads(r.embedding_vector) for r in results}

    def delete_memory(self, memory_id: str):
        with self.SessionLocal() as session:
            session.query(MemoryDB).filter(MemoryDB.id == memory_id).delete()
            session.query(MemoryEmbeddingDB).filter(MemoryEmbeddingDB.memory_id == memory_id).delete()
            session.commit()

    def update_last_accessed(self, memory_ids: List[str]):
        with self.SessionLocal() as session:
            for mid in memory_ids:
                mem = session.query(MemoryDB).filter(MemoryDB.id == mid).first()
                if mem:
                    mem.last_accessed = datetime.now(timezone.utc)
                self._log_access(session, mid)
            session.commit()

    def _log_access(self, session: Session, memory_id: str, context: str = None):
        log = MemoryAccessLogDB(memory_id=memory_id, context=context)
        session.add(log)

    def prune_memories(self, max_age_days: int = 30, max_capacity: Optional[int] = None) -> int:
        """
        Prunes decayed low-importance memories to prevent database bloat.
        - Preserves PREFERENCE memories and HIGH/CRITICAL importance memories.
        - Deletes memories older than max_age_days if importance is LOW.
        - Enforces max_capacity if specified by removing oldest unaccessed LOW/MEDIUM items.
        """
        from datetime import timedelta
        pruned_count = 0
        now = datetime.now(timezone.utc)
        with self.SessionLocal() as session:
            # 1. Age-based decay
            cutoff_date = now - timedelta(days=max_age_days)
            decay_query = session.query(MemoryDB).filter(
                MemoryDB.type != MemoryType.PREFERENCE.value,
                MemoryDB.importance == ImportanceLevel.LOW.value,
                MemoryDB.last_accessed < cutoff_date
            )
            expired_ids = [m.id for m in decay_query.all()]
            for mid in expired_ids:
                session.query(MemoryEmbeddingDB).filter(MemoryEmbeddingDB.memory_id == mid).delete()
                session.query(MemoryAccessLogDB).filter(MemoryAccessLogDB.memory_id == mid).delete()
                session.query(MemoryDB).filter(MemoryDB.id == mid).delete()
                pruned_count += 1
                
            # 2. Capacity-based pruning
            if max_capacity:
                total = session.query(MemoryDB).count()
                if total > max_capacity:
                    overflow = total - max_capacity
                    overflow_query = session.query(MemoryDB).filter(
                        MemoryDB.type != MemoryType.PREFERENCE.value,
                        MemoryDB.importance.in_([ImportanceLevel.LOW.value, ImportanceLevel.MEDIUM.value])
                    ).order_by(MemoryDB.last_accessed.asc()).limit(overflow)
                    
                    for m in overflow_query.all():
                        session.query(MemoryEmbeddingDB).filter(MemoryEmbeddingDB.memory_id == m.id).delete()
                        session.query(MemoryAccessLogDB).filter(MemoryAccessLogDB.memory_id == m.id).delete()
                        session.query(MemoryDB).filter(MemoryDB.id == m.id).delete()
                        pruned_count += 1
                        
            session.commit()
            return pruned_count

    def _to_pydantic(self, db_mem: MemoryDB) -> MemoryRecord:
        return MemoryRecord(
            id=db_mem.id,
            type=MemoryType(db_mem.type),
            content=db_mem.content,
            importance=ImportanceLevel(db_mem.importance),
            created_at=db_mem.created_at,
            last_accessed=db_mem.last_accessed,
            tags=json.loads(db_mem.tags) if db_mem.tags else []
        )

