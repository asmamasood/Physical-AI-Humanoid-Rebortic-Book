from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

print(f"Connecting to Qdrant: {QdrantClient}")
try:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Client initialized type:", type(client))
    print("Has search?", hasattr(client, "search"))
    print("Has query_points?", hasattr(client, "query_points"))
    print("Dir:", [d for d in dir(client) if not d.startswith("_")])
except Exception as e:
    print("Error:", e)
