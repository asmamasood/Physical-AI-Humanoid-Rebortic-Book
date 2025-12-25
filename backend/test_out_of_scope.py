import requests
import requests
# from termcolor import cprint

BASE_URL = "http://localhost:8000/api"

def print_result(feature, passed, details=None):
    if passed:
        print(f"✅ {feature}: PASSED")
    else:
        print(f"❌ {feature}: FAILED")
    if details:
        print(details)

def test_out_of_scope():
    print("\nTesting OUT OF SCOPE query...")
    # Query about something clearly not in the book (e.g., cooking or politics)
    payload = {
        "query": "How do I bake a cake?",
        "history": [],
        "session_id": "test-scope-session"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "")
        print(f"Response: {answer[:100]}...")
        
        # Check if response politely refuses
        if "sorry" in answer.lower() or "couldn't find" in answer.lower() or "book" in answer.lower():
            print_result("Out of Scope Restriction", True)
        else:
            print_result("Out of Scope Restriction", False, f"Response was too helpful: {answer}")
    except Exception as e:
        print_result("Out of Scope Restriction", False, str(e))

def test_in_scope():
    print("\nTesting IN SCOPE query...")
    payload = {
        "query": "What are ROS 2 nodes?",
        "history": [],
        "session_id": "test-scope-session"
    }
    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "")
        print(f"Response: {answer[:100]}...")
        
        if "ROS 2" in answer and len(answer) > 50:
            print_result("In Scope Query", True)
        else:
            print_result("In Scope Query", False, "Response was unresponsive or irrelevant.")
    except Exception as e:
        print_result("In Scope Query", False, str(e))

if __name__ == "__main__":
    test_out_of_scope()
    test_in_scope()
