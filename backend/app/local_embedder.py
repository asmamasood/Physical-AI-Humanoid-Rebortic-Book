"""
Local embedding client for RAG Chatboard.

Provides async embedding functionality using sentence-transformers (all-MiniLM-L6-v2).
"""

import asyncio
from typing import List
from functools import lru_cache
from sentence_transformers import SentenceTransformer

# Model configuration
# all-MiniLM-L6-v2 is a common, fast, and high-quality local embedding model.
# Dimension: 384
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

class LocalEmbedder:
    """
    Async wrapper for local sentence-transformers embedding.
    """
    
    def __init__(self, model_name: str = LOCAL_MODEL_NAME):
        """
        Initialize the local model.
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = EMBEDDING_DIMENSION
        
    async def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query for search.
        """
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(text, convert_to_numpy=True).tolist()
        )
        return embedding
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents for indexing.
        """
        if not texts:
            return []
            
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(texts, convert_to_numpy=True).tolist()
        )
        return embeddings

@lru_cache()
def get_local_embedder() -> LocalEmbedder:
    """Get cached local embedder instance."""
    return LocalEmbedder()

# Convenience function for dependency injection
async def embed_query(text: str) -> List[float]:
    """Embed a query using the default local embedder."""
    embedder = get_local_embedder()
    return await embedder.embed_query(text)
