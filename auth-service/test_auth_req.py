import requests
import json

base_url = "http://localhost:3001/api/auth"

headers = {
    "Origin": "http://localhost:3000",
    "Content-Type": "application/json"
}

print("Testing GET session...")
try:
    res = requests.get(f"{base_url}/session", headers=headers, timeout=5)
    print(f"GET Status: {res.status_code}")
    print(f"GET Response: {res.text[:200]}")
except Exception as e:
    print(f"GET Error: {e}")

print("\nTesting POST sign-in...")
try:
    data = {"email": "test@test.com", "password": "pass"}
    res = requests.post(f"{base_url}/sign-in/email", headers=headers, json=data, timeout=5)
    print(f"POST Status: {res.status_code}")
    print(f"POST Response: {res.text[:200]}")
except Exception as e:
    print(f"POST Error: {e}")
