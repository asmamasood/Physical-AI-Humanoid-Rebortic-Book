import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load env variables (assuming script run from root with python -m)
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "book_v1")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("Error: QDRANT_URL or QDRANT_API_KEY not set.")
    sys.exit(1)

print(f"Connecting to Qdrant...")
try:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    if client.collection_exists(COLLECTION_NAME):
        print(f"Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
        print("Deletion successful.")
    else:
        print(f"Collection '{COLLECTION_NAME}' does not exist.")
        
except Exception as e:
    print(f"Error resetting collection: {e}")
