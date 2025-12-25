"""
Cohere embedding client for RAG Chatboard.

Provides async embedding functionality using Cohere's embed-english-v3.0 model.
"""

import cohere
from typing import List
import asyncio
from functools import lru_cache

from .config import get_settings


# Cohere model configuration
COHERE_MODEL = "embed-english-v3.0"
EMBEDDING_DIMENSION = 1024


class CohereEmbedder:
    """
    Async wrapper for Cohere embedding API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Cohere client.
        
        Args:
            api_key: Cohere API key (uses settings if not provided)
        """
        if api_key is None:
            settings = get_settings()
            api_key = settings.cohere_api_key
        
        self.client = cohere.Client(api_key)
        self.model = COHERE_MODEL
    
    async def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query for search.
        
        Uses input_type="search_query" for optimal retrieval performance.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Run synchronous Cohere call in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_query"
            )
        )
        
        return response.embeddings[0]
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents for indexing.
        
        Uses input_type="search_document" for optimal indexing.
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Run synchronous Cohere call in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
        )
        
        return response.embeddings


@lru_cache()
def get_cohere_embedder() -> CohereEmbedder:
    """Get cached Cohere embedder instance."""
    return CohereEmbedder()


# Convenience function for dependency injection
async def embed_query(text: str) -> List[float]:
    """Embed a query using the default embedder."""
    embedder = get_cohere_embedder()
    return await embedder.embed_query(text)
