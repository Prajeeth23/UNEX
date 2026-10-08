import uuid
from typing import List, Dict
import aiohttp
from src.rag.vector_store import VectorStore
from qdrant_client.models import PointStruct

class DocumentIndexer:
    """Chunks text and generates embeddings to store in Qdrant."""
    def __init__(self, store: VectorStore):
        self.store = store
        from src.llm.ollama_client import OllamaProvider
        self.provider = OllamaProvider() # we will reuse it or write a small embedder
        
    async def index_text(self, text: str, source_metadata: Dict[str, str]):
        """Splits text, embeds it, and inserts it into Qdrant."""
        chunks = self._chunk_text(text)
        
        points = []
        for i, chunk in enumerate(chunks):
            embedding = await self._get_embedding(chunk)
            if embedding:
                point_id = str(uuid.uuid4())
                payload = {
                    "text": chunk,
                    "chunk_index": i,
                    **source_metadata
                }
                points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
                
        if points:
            self.store.insert(points)
            print(f"[DocumentIndexer] Indexed {len(points)} chunks from {source_metadata.get('source', 'Unknown')}.")
            
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
        
    async def _get_embedding(self, text: str) -> List[float]:
        # Utilizing Ollama's embedding endpoint natively
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"model": "nomic-embed-text", "prompt": text}
                base_url = getattr(self.provider, "base_url", getattr(self.provider, "host", "http://localhost:11434"))
                async with session.post(f"{base_url}/api/embeddings", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("embedding", [])
        except Exception as e:
            print(f"[DocumentIndexer] Embedding failed: {e}")
        return []
