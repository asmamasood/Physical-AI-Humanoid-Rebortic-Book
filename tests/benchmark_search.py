import os
import asyncio
import cohere
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

async def benchmark():
    co = cohere.Client(os.getenv("COHERE_API_KEY"))
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    collection_name = os.getenv("QDRANT_COLLECTION", "book_v1")
    
    query = "What is Physical AI?"
    print(f"Query: {query}")
    
    # Embed
    response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    vector = response.embeddings[0]
    
    # Search WITHOUT threshold first to see what we get
    print("\nSearch results (No threshold):")
    results = client.query_points(
        collection_name=collection_name,
        query=vector,
        limit=5,
        with_payload=True
    ).points
    
    if not results:
        print("No results found at all!")
    for r in results:
        print(f"Score: {r.score:.4f} | Chapter: {r.payload.get('chapter')} | Content: {r.payload.get('content')[:100]}...")

if __name__ == "__main__":
    asyncio.run(benchmark())
