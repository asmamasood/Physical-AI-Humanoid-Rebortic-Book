import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_regular_chat():
    print("\n=== Testing Regular Chat ===")
    payload = {
        "query": "what is ros2",
        "history": [],
        "session_id": "test-session-123"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_summarize_skill():
    print("\n=== Testing Summarize Skill ===")
    payload = {
        "query": "module 1 summary",
        "history": [],
        "session_id": "test-session-123",
        "module_id": "module-1",
        "chapter_id": None
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_quiz_skill():
    print("\n=== Testing Quiz Skill ===")
    payload = {
        "query": "quiz on module 1",
        "history": [],
        "session_id": "test-session-123",
        "module_id": "module-1",
        "chapter_id": None
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_regular_chat()
    test_summarize_skill()
    test_quiz_skill()
