import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_chat(payload):
    print(f"\nTesting: {payload.get('query')} (Intent: {payload.get('selected_text', 'N/A')})")
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
        print(f"Citations: {len(data['citations'])}")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

# 1. Test Summary
test_chat({"query": "summarize module 1", "user_id": "test_senior"})

# 2. Test Quiz
test_chat({"query": "generate a quiz for chapter 1", "user_id": "test_senior"})

# 3. Test Selective mode (Strict)
test_chat({
    "query": "What is the main topic?",
    "selected_text": "Physical AI focus on robots with meaningful interactions in physical world.",
    "user_id": "test_senior"
})

# 4. Test Selective mode (NotFound fallback)
test_chat({
    "query": "What is the capital of France?",
    "selected_text": "Robots use sensors to perceive the environment.",
    "user_id": "test_senior"
})
