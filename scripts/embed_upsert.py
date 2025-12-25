"""
Embed chunks using Cohere and upsert to Qdrant.

This script embeds text chunks using Cohere's embed-english-v3.0 model
and stores them in Qdrant Cloud with full metadata.
"""

import os
from typing import List
from dataclasses import asdict

import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    CollectionInfo,
)

from .chunker import Chunk


# Cohere embedding model - 1024 dimensions
COHERE_MODEL = "embed-english-v3.0"
COHERE_DIMENSION = 1024

# Local Model defaults - 384 dimensions
LOCAL_MODEL = "all-MiniLM-L6-v2"
LOCAL_DIMENSION = 384

BATCH_SIZE_COHERE = 96
BATCH_SIZE_LOCAL = 256


def get_cohere_client() -> cohere.Client:
    """Initialize Cohere client from environment."""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise ValueError("COHERE_API_KEY environment variable not set")
    return cohere.Client(api_key)


def get_local_embedder():
    """Import and return local embedder from backend app."""
    import sys
    from pathlib import Path
    
    # Ensure backend path is included
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    from backend.app.local_embedder import get_local_embedder
    return get_local_embedder()


def get_qdrant_client() -> QdrantClient:
    """Initialize Qdrant client from environment."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not url:
        raise ValueError("QDRANT_URL environment variable not set")
    if not api_key:
        raise ValueError("QDRANT_API_KEY environment variable not set")
    
    return QdrantClient(url=url, api_key=api_key)


def ensure_collection_exists(
    qdrant: QdrantClient,
    collection_name: str,
    vector_size: int
) -> bool:
    """
    Ensure the Qdrant collection exists, create if not.
    """
    collections = qdrant.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if collection_name in collection_names:
        # Check if dimension matches
        info = qdrant.get_collection(collection_name)
        current_size = info.config.params.vectors.size
        if current_size != vector_size:
            print(f"  Collection '{collection_name}' exists but has dimension {current_size} (Expected {vector_size})")
            print(f"  Recreating collection '{collection_name}'...")
            qdrant.delete_collection(collection_name)
        else:
            print(f"  Collection '{collection_name}' already exists with correct dimension {current_size}")
            return False
    
    print(f"  Creating collection '{collection_name}' with size {vector_size}...")
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    print(f"  Collection '{collection_name}' created")
    return True


def embed_texts(texts: List[str], provider: str = "local") -> List[List[float]]:
    """
    Embed a batch of texts using the selected provider.
    """
    if provider == "local":
        model = get_local_embedder()
        # Sentence Transformer's encode is synchronous
        return model.model.encode(texts, convert_to_numpy=True).tolist()
    else:
        co = get_cohere_client()
        response = co.embed(
            texts=texts,
            model=COHERE_MODEL,
            input_type="search_document"
        )
        return response.embeddings


def chunks_to_points(chunks: List[Chunk], embeddings: List[List[float]]) -> List[PointStruct]:
    """
    Convert chunks and embeddings to Qdrant PointStruct objects.
    """
    points = []
    
    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=chunk.chunk_id,
            vector=embedding,
            payload={
                "module": chunk.module,
                "chapter": chunk.chapter,
                "content": chunk.content,
                "source_url": chunk.source_url,
                "start_pos": chunk.start_pos,
                "end_pos": chunk.end_pos,
                "token_count": chunk.token_count
            }
        )
        points.append(point)
    
    return points


def embed_and_upsert(
    chunks: List[Chunk],
    collection_name: str = None
) -> int:
    """
    Embed chunks via Cohere and upsert to Qdrant.
    
    Args:
        chunks: List of Chunk objects to embed and store
        collection_name: Qdrant collection name (defaults to QDRANT_COLLECTION env var)
        
    Returns:
        Number of vectors upserted
    """
    if not chunks:
        print("  No chunks to process")
        return 0
    
    # Get collection name from env if not provided
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION", "book_v1_local")
    
    # Initialize clients
    print("  Initializing clients...")
    # Select dimension based on provider
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    vector_size = LOCAL_DIMENSION if provider == "local" else COHERE_DIMENSION
    
    qdrant = get_qdrant_client()
    
    # Ensure collection exists
    ensure_collection_exists(qdrant, collection_name, vector_size=vector_size)
    
    # Process in batches
    total_upserted = 0
    batch_size = BATCH_SIZE_LOCAL if provider == "local" else BATCH_SIZE_COHERE
    num_batches = (len(chunks) + batch_size - 1) // batch_size
    
    print(f"  Embedding and upserting {len(chunks)} chunks in {num_batches} batches...")
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_texts = [c.content for c in batch_chunks]
        batch_num = i // batch_size + 1
        
        print(f"    Batch {batch_num}/{num_batches}: embedding {len(batch_chunks)} chunks...")
        
        # Embed batch
        try:
            embeddings = embed_texts(batch_texts, provider=provider)
            if embeddings:
                print(f"    Batch {batch_num}: embedded {len(embeddings)} chunks. Dimension: {len(embeddings[0])}")
        except Exception as e:
            print(f"    Error embedding batch {batch_num}: {e}")
            continue
        
        # Convert to points
        points = chunks_to_points(batch_chunks, embeddings)
        
        # Upsert to Qdrant
        try:
            qdrant.upsert(
                collection_name=collection_name,
                points=points
            )
            total_upserted += len(points)
            print(f"    Batch {batch_num}: upserted {len(points)} vectors")
        except Exception as e:
            print(f"    Error upserting batch {batch_num}: {e}")
            continue
    
    print(f"  Total vectors upserted: {total_upserted}")
    return total_upserted


def get_collection_stats(collection_name: str = None) -> dict:
    """
    Get statistics about the Qdrant collection.
    """
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION", "book_v1_local")
    
    qdrant = get_qdrant_client()
    
    try:
        info = qdrant.get_collection(collection_name)
        return {
            "collection": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value if info.status else "unknown"
        }
    except Exception as e:
        return {
            "collection": collection_name,
            "error": str(e)
        }


def main():
    """Test embedding and upserting with sample data."""
    from pathlib import Path
    from dotenv import load_dotenv
    
    # Load environment
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    load_dotenv(project_root / ".env")
    
    print("Testing embed_upsert module...")
    
    # Check environment
    required_vars = ["COHERE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"Missing environment variables: {missing}")
        print("Please set these in .env file")
        return
    
    # Get collection stats
    stats = get_collection_stats()
    print(f"Collection stats: {stats}")


if __name__ == "__main__":
    main()
