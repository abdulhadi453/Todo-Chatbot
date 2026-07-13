#!/usr/bin/env python3
"""
Complete end-to-end test of auth and data persistence.
This will verify that all fixes are working correctly.
"""

import sys
import os
import requests
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123!"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def test_signup(email, password, name="Test User"):
    """Test user signup."""
    print(f"\n[TEST] Signing up: {email}")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password, "name": name},
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            print(f"[PASS] Signup successful")
            print(f"  User ID: {data.get('id', 'MISSING')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Token: {data.get('access_token', 'MISSING')[:30]}...")
            return data
        elif response.status_code == 409:
            print(f"[INFO] User already exists (expected)")
            return None
        else:
            print(f"[FAIL] Signup failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Signup exception: {str(e)}")
        return None

def test_login(email, password):
    """Test user login."""
    print(f"\n[TEST] Logging in: {email}")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Login successful")
            print(f"  User ID: {data.get('id', 'MISSING')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Token: {data.get('access_token', 'MISSING')[:30]}...")
            return data
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Login exception: {str(e)}")
        return None

def test_create_task(user_id, token, title):
    """Test creating a task."""
    print(f"\n[TEST] Creating task: {title}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/{user_id}/todos",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": title, "description": "Test task", "completed": False},
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            print(f"[PASS] Task created")
            print(f"  Task ID: {data.get('id')}")
            print(f"  Title: {data.get('title')}")
            return data
        else:
            print(f"[FAIL] Task creation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Task creation exception: {str(e)}")
        return None

def test_get_tasks(user_id, token):
    """Test getting tasks."""
    print(f"\n[TEST] Getting tasks for user")

    try:
        response = requests.get(
            f"{BASE_URL}/api/{user_id}/todos",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            task_count = len(data) if isinstance(data, list) else 0
            print(f"[PASS] Retrieved {task_count} tasks")
            for task in (data if isinstance(data, list) else []):
                print(f"  - {task.get('title')} (ID: {task.get('id')})")
            return data
        else:
            print(f"[FAIL] Get tasks failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Get tasks exception: {str(e)}")
        return None

def test_chat(user_id, token, message):
    """Test chat endpoint."""
    print(f"\n[TEST] Sending chat message: {message}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/{user_id}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": message},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Chat response received")
            print(f"  Response: {data.get('response', '')[:100]}...")
            return data
        else:
            print(f"[FAIL] Chat failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Chat exception: {str(e)}")
        return None

def main():
    print_section("END-TO-END AUTH & DATA PERSISTENCE TEST")

    # Test 1: Check backend is running
    print_section("TEST 1: Backend Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[PASS] Backend is running")
        else:
            print("[FAIL] Backend returned unexpected status")
            return
    except Exception as e:
        print(f"[FAIL] Backend is not running: {str(e)}")
        print("\nPlease start the backend first:")
        print("  cd backend")
        print("  python run_server.py")
        return

    # Test 2: Login (or signup if needed)
    print_section("TEST 2: Login Flow")
    auth_data = test_login(TEST_EMAIL, TEST_PASSWORD)

    if not auth_data:
        print("\n[INFO] Login failed, trying signup...")
        auth_data = test_signup(TEST_EMAIL, TEST_PASSWORD)

        if not auth_data:
            print("[FAIL] Both login and signup failed")
            return

    user_id = auth_data.get('id')
    token = auth_data.get('access_token')

    if not user_id or not token:
        print("[FAIL] Missing user_id or token in response")
        print(f"  user_id: {user_id}")
        print(f"  token: {'present' if token else 'MISSING'}")
        return

    # Test 3: Create tasks
    print_section("TEST 3: Create Tasks")
    task1 = test_create_task(user_id, token, "Test Task 1 - Buy groceries")
    task2 = test_create_task(user_id, token, "Test Task 2 - Write report")
    task3 = test_create_task(user_id, token, "Test Task 3 - Call client")

    created_tasks = [t for t in [task1, task2, task3] if t]
    print(f"\n[RESULT] Created {len(created_tasks)}/3 tasks")

    # Test 4: Retrieve tasks
    print_section("TEST 4: Retrieve Tasks (First Session)")
    tasks_before = test_get_tasks(user_id, token)

    # Test 5: Simulate logout/login cycle
    print_section("TEST 5: Logout and Login Again")
    print("[INFO] Simulating logout...")
    time.sleep(1)

    auth_data2 = test_login(TEST_EMAIL, TEST_PASSWORD)

    if not auth_data2:
        print("[FAIL] Cannot login after logout simulation")
        return

    token2 = auth_data2.get('access_token')

    # Test 6: Verify tasks persist
    print_section("TEST 6: Retrieve Tasks (After Re-login)")
    tasks_after = test_get_tasks(user_id, token2)

    # Test 7: Test chat
    print_section("TEST 7: Chat Feature")
    chat_result = test_chat(user_id, token2, "Hello, this is a test message")

    # Summary
    print_section("TEST SUMMARY")

    tests = {
        "Backend Running": response.status_code == 200,
        "Login/Signup": auth_data is not None,
        "User ID Present": user_id is not None and user_id != 'MISSING',
        "Token Present": token is not None and token != 'MISSING',
        "Tasks Created": len(created_tasks) >= 1,
        "Tasks Retrieved (Before)": tasks_before is not None,
        "Re-login Works": auth_data2 is not None,
        "Tasks Persist (After)": tasks_after is not None and len(tasks_after) == len(tasks_before) if tasks_before and tasks_after else False,
        "Chat Works": chat_result is not None
    }

    passed = sum(1 for v in tests.values() if v)
    total = len(tests)

    print(f"\nTests Passed: {passed}/{total}\n")

    for test_name, result in tests.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nYour auth system and data persistence are working correctly.")
        print("You can now:")
        print("  1. Login/logout without losing data")
        print("  2. Create tasks that persist across sessions")
        print("  3. Use the chat feature")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        print("Please check the details above and restart the backend if needed.")

if __name__ == "__main__":
    main()
