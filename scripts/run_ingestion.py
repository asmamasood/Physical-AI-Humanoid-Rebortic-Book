"""
Main ingestion orchestration script.

Run this script to ingest all Docusaurus chapters into Qdrant.
"""

import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class IngestionResult:
    """Results from an ingestion run."""
    files_processed: int
    chapters_collected: int
    chunks_created: int
    vectors_upserted: int
    duration_seconds: float
    errors: list


def validate_environment() -> list:
    """
    Validate all required environment variables are set.
    
    Returns list of missing variables.
    """
    required = [
        "COHERE_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
    ]
    
    missing = [var for var in required if not os.getenv(var)]
    return missing


def run_ingestion(
    docs_path: Optional[Path] = None,
    collection_name: Optional[str] = None,
    min_tokens: int = 200,
    max_tokens: int = 800,
    overlap_sentences: int = 2
) -> IngestionResult:
    """
    Run the full ingestion pipeline.
    
    Args:
        docs_path: Path to Docusaurus docs directory
        collection_name: Qdrant collection name
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
        overlap_sentences: Sentence overlap between chunks
        
    Returns:
        IngestionResult with statistics
    """
    start_time = time.time()
    errors = []
    
    # Import here to avoid circular imports
    from .collect_chapters import collect_chapters
    from .chunker import chunk_all_chapters
    from .embed_upsert import embed_and_upsert, get_collection_stats
    
    # Determine docs path
    if docs_path is None:
        docs_path_str = os.getenv("DOCS_PATH", "physical-ai-robotics-book/docs")
        # Handle relative paths
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        docs_path = project_root / docs_path_str
    
    # Get collection name from env if not provided
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION", "book_v1_local")
    
    # Get chunking parameters from env
    min_tokens = int(os.getenv("CHUNK_MIN_TOKENS", min_tokens))
    max_tokens = int(os.getenv("CHUNK_MAX_TOKENS", max_tokens))
    overlap_sentences = int(os.getenv("CHUNK_OVERLAP_SENTENCES", overlap_sentences))
    
    print("=" * 60)
    print("RAG Chatboard Ingestion Pipeline")
    print("=" * 60)
    print(f"Docs path: {docs_path}")
    print(f"Collection: {collection_name}")
    print(f"Chunking: {min_tokens}-{max_tokens} tokens, {overlap_sentences} sentence overlap")
    print()
    
    # Step 1: Collect chapters
    print("Step 1: Collecting chapters...")
    try:
        # Collect from Docs
        chapters = collect_chapters(
            docs_path, 
            url_prefix="/docs/"
        )
        print(f"  -> Docs: {len(chapters)} chapters")
        
        # Collect from Blog
        blog_path = docs_path.parent / "blog"
        if blog_path.exists():
            blog_chapters = collect_chapters(
                blog_path,
                url_prefix="/blog/",
                fixed_module="blog"
            )
            print(f"  -> Blog: {len(blog_chapters)} posts")
            chapters.extend(blog_chapters)
        
        chapters_collected = len(chapters)
        print(f"  -> Total Collected: {chapters_collected} items")
    except Exception as e:
        errors.append(f"Chapter collection failed: {e}")
        print(f"  ERROR: {e}")
        return IngestionResult(
            files_processed=0,
            chapters_collected=0,
            chunks_created=0,
            vectors_upserted=0,
            duration_seconds=time.time() - start_time,
            errors=errors
        )
    
    if chapters_collected == 0:
        print("  No chapters found. Exiting.")
        return IngestionResult(
            files_processed=0,
            chapters_collected=0,
            chunks_created=0,
            vectors_upserted=0,
            duration_seconds=time.time() - start_time,
            errors=["No chapters found in docs directory"]
        )
    
    # Step 2: Chunk chapters
    print("\nStep 2: Chunking chapters...")
    try:
        chunks = chunk_all_chapters(
            chapters,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            overlap_sentences=overlap_sentences
        )
        chunks_created = len(chunks)
        print(f"  -> Created {chunks_created} chunks")
    except Exception as e:
        errors.append(f"Chunking failed: {e}")
        print(f"  ERROR: {e}")
        return IngestionResult(
            files_processed=chapters_collected,
            chapters_collected=chapters_collected,
            chunks_created=0,
            vectors_upserted=0,
            duration_seconds=time.time() - start_time,
            errors=errors
        )
    
    # Step 3: Embed and upsert
    print("\nStep 3: Embedding and upserting to Qdrant...")
    try:
        vectors_upserted = embed_and_upsert(chunks, collection_name)
        print(f"  -> Upserted {vectors_upserted} vectors")
    except Exception as e:
        errors.append(f"Embed/upsert failed: {e}")
        print(f"  ERROR: {e}")
        vectors_upserted = 0
    
    # Get final stats
    print("\nStep 4: Verifying collection...")
    stats = get_collection_stats(collection_name)
    print(f"  Collection stats: {stats}")
    
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("Ingestion Complete")
    print("=" * 60)
    print(f"Chapters collected: {chapters_collected}")
    print(f"Chunks created: {chunks_created}")
    print(f"Vectors upserted: {vectors_upserted}")
    print(f"Duration: {duration:.2f} seconds")
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors:
            print(f"  - {err}")
    
    return IngestionResult(
        files_processed=chapters_collected,
        chapters_collected=chapters_collected,
        chunks_created=chunks_created,
        vectors_upserted=vectors_upserted,
        duration_seconds=duration,
        errors=errors
    )


def main():
    """Main entry point for ingestion script."""
    # Find project root and load environment
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Load .env file
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")
    else:
        print(f"Warning: No .env file found at {env_path}")
        print("Make sure environment variables are set")
    
    # Validate environment
    missing = validate_environment()
    if missing:
        print(f"\nError: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        sys.exit(1)
    
    # Run ingestion
    result = run_ingestion()
    
    # Exit with appropriate code
    if result.errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
