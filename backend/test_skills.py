import requests
import json

def test_summary():
    url = "http://localhost:8000/api/chat"
    payload = {
        "query": "Summarize this page 📖 (Context: Introduction to ROS 2, URL: /docs/module-1/chapter-1)",
        "session_id": "test_session",
        "user_id": "test_user",
        "module_id": "module-1",
        "chapter_id": "chapter-1"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            try:
                print(f"Detail: {response.json().get('detail', 'No detail')}")
            except:
                print(f"Text: {response.text[:200]}")
        else:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_summary()
