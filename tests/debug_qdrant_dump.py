import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
collection_name = os.getenv("QDRANT_COLLECTION", "book_v1")

try:
    print(f"Dumping points from {collection_name}...")
    # Scroll to get points
    # (Using client.scroll as client.search/query_points might not show everything easily)
    points, _ = client.scroll(
        collection_name=collection_name,
        limit=5,
        with_payload=True,
        with_vectors=False
    )
    
    for p in points:
        print(f"--- Point ID: {p.id} ---")
        print(f"Payload: {p.payload}")
        print()
        
except Exception as e:
    print(f"Error: {e}")
