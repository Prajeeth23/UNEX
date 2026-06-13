import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, collection_name: str = "unex_knowledge"):
        self.collection_name = collection_name
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_db"))
        os.makedirs(self.db_path, exist_ok=True)
        
        # Local Qdrant Engine
        self.client = QdrantClient(path=self.db_path)
        
        # Ollama nomic-embed-text generates 768-dimensional embeddings
        self.vector_size = 768 
        
        self._ensure_collection()
        
    def _ensure_collection(self):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            print(f"[VectorStore] Created collection: {self.collection_name}")
            
    def insert(self, points: List[PointStruct]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in results]
