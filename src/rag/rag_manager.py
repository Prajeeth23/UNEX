from src.rag.vector_store import VectorStore
from src.rag.document_indexer import DocumentIndexer
from typing import List, Dict, Any

class RAGManager:
    def __init__(self):
        self.store = VectorStore()
        self.indexer = DocumentIndexer(self.store)
        
    async def index_file(self, filepath: str, source_metadata: Dict[str, str] = None):
        """Reads a file and indexes it."""
        import os
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
        meta = source_metadata or {"source": filepath}
        await self.indexer.index_text(text, meta)
        
    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Embeds query and searches Qdrant."""
        embedding = await self.indexer._get_embedding(query)
        if not embedding:
            return []
            
        results = self.store.search(embedding, limit=limit)
        return results
