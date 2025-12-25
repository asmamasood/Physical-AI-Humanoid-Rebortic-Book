import requests
import json
import traceback

BASE_URL = "http://localhost:8000/api"

def test_chat_with_full_error():
    print("\n=== Testing Chat with Full Error Details ===")
    payload = {
        "query": "what is ros2",
        "history": [],
        "session_id": "test-session-debug"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        print(f"Status Code: {res.status_code}")
        print(f"Headers: {dict(res.headers)}")
        print(f"\nFull Response:")
        print(json.dumps(res.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"General Error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_chat_with_full_error()
