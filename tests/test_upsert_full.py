import os
from scripts.chunker import Chapter, chunk_chapter
from scripts.embed_upsert import embed_and_upsert
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

# Sample data
chapter = Chapter(
    path=Path("test.md"),
    module="test",
    title="Test Chapter",
    content="Physical AI is the integration of AI into physical systems like robots. It allows machines to interact with the world.",
    source_url="http://localhost:3000/test"
)

print("Chunking...")
# Use lower limits to ensure chunks are created
chunks = chunk_chapter(chapter, min_tokens=10, max_tokens=100)
print(f"Chunks created: {len(chunks)}")

if chunks:
    print("Attempting to embed and upsert...")
    try:
        count = embed_and_upsert(chunks, collection_name="test_debug_upsert")
        print(f"Successfully upserted: {count}")
    except Exception as e:
        print(f"FAILED with exception: {e}")
else:
    print("No chunks created. Check chunking logic.")
