import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
collection_name = os.getenv("QDRANT_COLLECTION", "book_v1")

try:
    info = client.get_collection(collection_name)
    print(f"Collection: {collection_name}")
    print(f"Status: {info.status}")
    print(f"Configuration: {info.config}")
    print(f"Vector size: {info.config.params.vectors.size}")
    
    print(f"Deleting collection {collection_name}...")
    client.delete_collection(collection_name)
    print("Deleted.")
except Exception as e:
    print(f"Error: {e}")
