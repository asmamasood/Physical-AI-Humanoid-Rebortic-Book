import asyncio
import requests
import json
# from termcolor import cprint 

BASE_URL = "http://localhost:8000/api"

def print_result(feature, passed, details=None):
    if passed:
        print(f"✅ {feature}: PASSED")
    else:
        print(f"❌ {feature}: FAILED")
    if details:
        print(details)

def test_summary():
    print("\nTesting SUMMARY intent...")
    payload = {
        "query": "summarize the concept of ROS 2 nodes",
        "history": [],
        "session_id": "test-feature-session"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "")
        print(f"Response: {answer[:100]}...")
        
        # Check if response looks like a summary
        if "summary" in answer.lower() or len(answer) > 50:
            print_result("Summary Feature", True)
        else:
            print_result("Summary Feature", False, "Response too short or irrelevant.")
    except Exception as e:
        print_result("Summary Feature", False, str(e))

def test_quiz():
    print("\nTesting QUIZ intent...")
    payload = {
        "query": "quiz me on ROS 2 basics",
        "history": [],
        "session_id": "test-feature-session"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "")
        print(f"Response: {answer[:100]}...")
        
        # Check for quiz indicators like "Question 1" or "?"
        if "?" in answer or "Question" in answer:
            print_result("Quiz Feature", True)
        else:
            print_result("Quiz Feature", False, "Response does not look like a quiz.")
    except Exception as e:
        print_result("Quiz Feature", False, str(e))

def test_selected_text():
    print("\nTesting SELECTED TEXT mode...")
    payload = {
        "query": "explain this code",
        "selected_text": "rclpy.init(args=args)\nnode = MinimalPublisher()",
        "history": [],
        "session_id": "test-feature-session"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "")
        print(f"Response: {answer[:100]}...")
        
        # Check if response references the code
        if "init" in answer or "node" in answer or "Python" in answer:
            print_result("Selected Text Feature", True)
        else:
            print_result("Selected Text Feature", False, "Response didn't explain the code.")
    except Exception as e:
        print_result("Selected Text Feature", False, str(e))

if __name__ == "__main__":
    test_summary()
    test_quiz()
    test_selected_text()
