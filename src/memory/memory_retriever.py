from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple
from src.memory.memory_store import MemoryStore
from src.memory.memory_models import MemoryRecord

class MemoryRetriever:
    def __init__(self, memory_store: MemoryStore, model_name: str = "all-MiniLM-L6-v2"):
        self.memory_store = memory_store
        self.model = SentenceTransformer(model_name)
        self._cache_embeddings_matrix = None
        self._cache_memory_ids = None
        self._cache_db_norms = None
        self._cache_dirty = True
        
    def mark_dirty(self):
        """Called by MemoryManager when a memory is added or deleted."""
        self._cache_dirty = True
        
    def _refresh_cache(self):
        if not self._cache_dirty:
            return
            
        all_embeddings_dict = self.memory_store.get_all_embeddings()
        if not all_embeddings_dict:
            self._cache_memory_ids = []
            self._cache_embeddings_matrix = np.array([])
            self._cache_db_norms = np.array([])
        else:
            self._cache_memory_ids = list(all_embeddings_dict.keys())
            self._cache_embeddings_matrix = np.array(list(all_embeddings_dict.values()))
            db_norms = np.linalg.norm(self._cache_embeddings_matrix, axis=1)
            self._cache_db_norms = np.where(db_norms > 0, db_norms, 1e-10)
            
        self._cache_dirty = False
        
    def embed_text(self, text: str) -> list:
        # Convert to numpy array and back to list for JSON serialization
        return self.model.encode(text).tolist()

    def search(self, query: str, top_k: int = 5, min_score: float = 0.2) -> List[Tuple[MemoryRecord, float]]:
        self._refresh_cache()
        
        if len(self._cache_memory_ids) == 0:
            return []
            
        # Get query embedding
        query_emb = np.array(self.embed_text(query))
        query_norm = np.linalg.norm(query_emb)
        query_norm = query_norm if query_norm > 0 else 1e-10
        
        # Calculate cosine similarity using cached matrix
        similarities = np.dot(self._cache_embeddings_matrix, query_emb) / (self._cache_db_norms * query_norm)
        
        # Get top_k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score: # Configurable similarity threshold
                mem_id = self._cache_memory_ids[idx]
                mem_record = self.memory_store.get_memory(mem_id)
                if mem_record:
                    results.append((mem_record, score))
                    
        # Update last accessed for retrieved memories
        retrieved_ids = [mem.id for mem, _ in results]
        if retrieved_ids:
            self.memory_store.update_last_accessed(retrieved_ids)
            
        return results
