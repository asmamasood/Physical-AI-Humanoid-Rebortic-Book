import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat():
    print("Testing /api/chat...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "query": "What is a ROS 2 node?",
                "limit": 3
            }
        )
        if response.status_code == 200:
            print("Chat API Response:", json.dumps(response.json(), indent=2)[:200] + "...")
        else:
            print(f"Chat API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Chat API Connection Failed: {e}")

if __name__ == "__main__":
    test_chat()
