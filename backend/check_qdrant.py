from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

def check_qdrant():
    load_dotenv()
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection = os.getenv("QDRANT_COLLECTION", "book_v1_local")
    
    client = QdrantClient(url=url, api_key=api_key)
    
    print(f"Collection: {collection}")
    try:
        info = client.get_collection(collection)
        print(f"Points count: {info.points_count}")
        
        # Get one point to see payload
        points = client.scroll(collection_name=collection, limit=1, with_payload=True)[0]
        if points:
            print(f"Sample Payload: {points[0].payload}")
        else:
            print("No points found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_qdrant()
