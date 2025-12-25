import requests
import json
import traceback

BASE_URL = "http://localhost:8001/api"

def test_chat_verification():
    print(f"\n=== Testing Chat Verification on {BASE_URL} ===")
    payload = {
        "query": "what is ros2",
        "history": [],
        "session_id": "test-session-verify"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        print(f"Status Code: {res.status_code}")
        print(f"Headers: {dict(res.headers)}")
        
        if res.status_code == 200:
            print("\n✅ Verification SUCCESS! Response:")
            print(json.dumps(res.json(), indent=2))
        else:
            print("\n❌ Verification FAILED!")
            print(f"Full Response:")
            print(res.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"General Error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_chat_verification()
