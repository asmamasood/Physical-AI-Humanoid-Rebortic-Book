from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os
import uuid

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

try:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    COLLECTION = "test_debug"
    
    # Ensure collection exists
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE)
        )
        # Upsert a point
        client.upsert(
            collection_name=COLLECTION,
            points=[
                {
                    "id": str(uuid.uuid4()),
                    "vector": [0.1, 0.1, 0.1, 0.1],
                    "payload": {"test": "data"}
                }
            ]
        )

    # Query
    print("Calling query_points...")
    results = client.query_points(
        collection_name=COLLECTION,
        query=[0.1, 0.1, 0.1, 0.1],
        limit=1,
        with_payload=True
    )
    
    print(f"Result type: {type(results)}")
    print(f"Result content: {results}")

    if hasattr(results, 'points'):
        print("Has .points attribute")
    else:
        print("Does NOT have .points attribute")

except Exception as e:
    print(f"Error: {e}")
