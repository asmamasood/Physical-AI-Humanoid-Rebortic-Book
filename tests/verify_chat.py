import requests
import json

payload = {
    "query": "What is Physical AI?",
    "top_k": 3
}

try:
    response = requests.post("http://localhost:8000/api/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data.get('answer')}")
        print(f"Citations: {len(data.get('citations', []))}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Error: {e}")
