from qdrant_client import QdrantClient
print("QdrantClient imported")
client = QdrantClient(":memory:")
print("Client created")
print(f"Has search: {hasattr(client, 'search')}")
print(f"Has query_points: {hasattr(client, 'query_points')}")
print(f"Use query_points?: {'query_points' in dir(client)}")
print("Dir:", [d for d in dir(client) if 'search' in d or 'query' in d])
