
import requests
import random
import string
import sys

BASE_URL = "http://localhost:3001/api/auth"

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def test_auth_flow():
    email = generate_random_email()
    password = "password123"
    name = "Test User"
    
    print(f"Testing with email: {email}")
    session = requests.Session()
    
    # 1. Sign Up
    print("\n1. Testing Sign Up...")
    try:
        resp = session.post(f"{BASE_URL}/sign-up/email", json={
            "email": email,
            "password": password,
            "name": name
        })
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text[:100]}...")
        if resp.status_code != 200:
            print("   FAILED: Sign Up")
            return
        print("   PASSED: Sign Up")
    except Exception as e:
        print(f"   ERROR: {e}")
        return

    # 2. Check Session (auto login after signup usually)
    print("\n2. Checking Session (Post-Signup)...")
    resp = session.get(f"{BASE_URL}/get-session")
    print(f"   Status: {resp.status_code}")
    if resp.json():
        print("   PASSED: Session active")
    else:
        print("   WARNING: Session null after signup (might require manual signin)")
        
        # 3. Sign In
        print("\n3. Testing Sign In...")
        resp = session.post(f"{BASE_URL}/sign-in/email", json={
            "email": email,
            "password": password
        })
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
             print("   PASSED: Sign In")
        else:
             print("   FAILED: Sign In")
             return

    # 4. Sign Out
    print("\n4. Testing Sign Out...")
    resp = session.post(f"{BASE_URL}/sign-out", headers={"Origin": "http://localhost:3000"})
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print("   PASSED: Sign Out endpoint")
    else:
        print(f"   FAILED: Sign Out endpoint (status: {resp.status_code})")
        print(f"   Note: This might be due to CSRF protection, which is normal for browser-based auth")

    # 5. Check Session (Post-Signout)
    print("\n5. Checking Session (Post-Signout)...")
    resp = session.get(f"{BASE_URL}/get-session")
    data = resp.json()
    if data is None or data == "null" or not data:
        print("   PASSED: Session is null")
    else:
        print(f"   FAILED: Session still active: {data}")

if __name__ == "__main__":
    test_auth_flow()
