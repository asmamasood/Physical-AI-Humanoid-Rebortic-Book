import asyncio
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)

from .config import get_settings

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Async wrapper for Qdrant vector database operations.
    """
    
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = None
    ):
        """
        Initialize Qdrant client.
        
        Args:
            url: Qdrant Cloud URL
            api_key: Qdrant API key
            collection_name: Default collection name
        """
        settings = get_settings()
        
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        self.collection_name = collection_name or settings.qdrant_collection

        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )
    
    async def search_chunks(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_module: Optional[str] = None,
        filter_chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks in Qdrant with optional Module/Chapter filtering.
        """
        settings = get_settings()
        score_threshold = settings.score_threshold
        logger.info(f"Searching chunks with query_points: mod={filter_module}, ch={filter_chapter}")
        
        # Build filter conditions
        must_conditions = []
        if filter_module:
            must_conditions.append(FieldCondition(key="module", match=MatchValue(value=filter_module)))
        if filter_chapter:
            must_conditions.append(FieldCondition(key="chapter", match=MatchValue(value=filter_chapter)))
            
        query_filter = Filter(must=must_conditions) if must_conditions else None
        
        # Run synchronous Qdrant call in thread pool
        async def do_search(f):
            loop = asyncio.get_event_loop()
            try:
                # Use client.query_points as search is deprecated/removed
                # and more robust filter handling
                return await loop.run_in_executor(
                    None,
                    lambda: self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_embedding,
                        limit=top_k,
                        score_threshold=score_threshold,
                        query_filter=f,
                        with_payload=True
                    ).points
                )
            except Exception as search_err:
                logger.error(f"Qdrant search error with filter {f}: {search_err}")
                raise

        # Stage 1: Filtered Search
        try:
            results = await do_search(query_filter)
        except Exception:
            # If filtered search fails, immediately try wide search as emergency fallback
            logger.warning("Filtered search failed, trying wide search.")
            results = await do_search(None)
        
        # Handle results list
        final_points = results
        
        # Stage 2 Fallback: If no results, try without chapter filter
        if not final_points and filter_chapter:
            logger.info(f"Fallback: No results for ch={filter_chapter}. Retrying with mod={filter_module} only.")
            fallback_filter = Filter(must=[FieldCondition(key="module", match=MatchValue(value=filter_module))]) if filter_module else None
            results = await do_search(fallback_filter)
            final_points = results

        # Stage 3 Fallback: Still no results? Search everything
        if not final_points and (filter_module or filter_chapter):
            logger.info("Fallback: Still no results. performing wide search (no filters).")
            results = await do_search(None)
            final_points = results

        # Convert to dictionaries
        chunks = []
        for result in final_points:
            chunk = {
                "chunk_id": result.id,
                "score": result.score,
                **result.payload
            }
            chunks.append(chunk)
        
        return chunks
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        loop = asyncio.get_event_loop()
        
        try:
            info = await loop.run_in_executor(
                None,
                lambda: self.client.get_collection(self.collection_name)
            )
            
            return {
                "collection": self.collection_name,
                "vectors_count": info.vectors_count or 0,
                "points_count": info.points_count or 0,
                "status": info.status.value if info.status else "unknown"
            }
        except Exception as e:
            return {
                "collection": self.collection_name,
                "vectors_count": 0,
                "points_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def collection_exists(self) -> bool:
        """Check if the collection exists."""
        loop = asyncio.get_event_loop()
        
        try:
            collections = await loop.run_in_executor(
                None,
                lambda: self.client.get_collections()
            )
            return self.collection_name in [c.name for c in collections.collections]
        except Exception:
            return False


# @lru_cache()
def get_qdrant_service() -> QdrantService:
    """Get cached Qdrant service instance."""
    return QdrantService()


# Convenience function for dependency injection
async def search_chunks(
    query_embedding: List[float],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """Search chunks using the default Qdrant service."""
    service = get_qdrant_service()
    return await service.search_chunks(query_embedding, top_k=top_k)
