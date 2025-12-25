import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
active_collection = os.getenv("QDRANT_COLLECTION")

print(f"Active Collection in .env: {active_collection}")

q = QdrantClient(url=url, api_key=api_key)
collections = q.get_collections().collections

for c in collections:
    info = q.get_collection(c.name)
    size = info.config.params.vectors.size
    print(f"Collection: {c.name}, Dimension: {size}, Points: {info.points_count}")
