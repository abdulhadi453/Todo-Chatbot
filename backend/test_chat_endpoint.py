#!/usr/bin/env python3
"""
Test script to diagnose chat endpoint issues.
Run this while your backend is running to check if everything is configured correctly.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import jwt

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"
JWT_SECRET = "your-secret-key-here-change-this-for-production"  # From your .env

def print_test(test_name, passed, message=""):
    """Print test result with formatting."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status} - {test_name}")
    if message:
        print(f"   {message}")

def test_backend_running():
    """Test if backend is accessible."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print_test("Backend Running", True, f"Health check returned: {response.json()}")
            return True
        else:
            print_test("Backend Running", False, f"Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("Backend Running", False, "Cannot connect to backend. Is it running on port 8000?")
        return False
    except Exception as e:
        print_test("Backend Running", False, f"Error: {str(e)}")
        return False

def test_chat_endpoint_exists():
    """Test if chat endpoint is registered."""
    try:
        # Try without auth - should get 401 or 403, not 404
        response = requests.post(
            f"{BACKEND_URL}/api/{TEST_USER_ID}/chat",
            json={"message": "test"},
            timeout=5
        )
        if response.status_code == 404:
            print_test("Chat Endpoint Exists", False, "Endpoint not found (404)")
            return False
        elif response.status_code in [401, 403]:
            print_test("Chat Endpoint Exists", True, f"Endpoint exists (returned {response.status_code} - auth required)")
            return True
        else:
            print_test("Chat Endpoint Exists", True, f"Endpoint exists (returned {response.status_code})")
            return True
    except Exception as e:
        print_test("Chat Endpoint Exists", False, f"Error: {str(e)}")
        return False

def create_test_token(user_id, secret_key):
    """Create a test JWT token."""
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def test_chat_with_auth():
    """Test chat endpoint with authentication."""
    try:
        # Create a test token
        token = create_test_token(TEST_USER_ID, JWT_SECRET)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "message": "Hello, this is a test message"
        }

        response = requests.post(
            f"{BACKEND_URL}/api/{TEST_USER_ID}/chat",
            headers=headers,
            json=payload,
            timeout=30  # Chat can take time with OpenAI
        )

        if response.status_code == 200:
            data = response.json()
            print_test("Chat With Auth", True, f"Got response: {data.get('response', '')[:100]}...")
            return True
        elif response.status_code == 401:
            print_test("Chat With Auth", False, f"Auth failed: {response.json().get('detail', 'Unknown error')}")
            print("   NOTE: This might be because the test user doesn't exist in the database")
            return False
        else:
            print_test("Chat With Auth", False, f"Status {response.status_code}: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print_test("Chat With Auth", False, "Request timed out (OpenAI might be slow or failing)")
        return False
    except Exception as e:
        print_test("Chat With Auth", False, f"Error: {str(e)}")
        return False

def test_openai_config():
    """Check if OpenAI API key is configured."""
    try:
        import os
        from dotenv import load_dotenv

        # Load .env file
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("AGENT_MODEL_NAME", "gpt-3.5-turbo")

        if api_key and len(api_key) > 20:
            print_test("OpenAI Config", True, f"API key configured (length: {len(api_key)}), Model: {model}")
            return True
        else:
            print_test("OpenAI Config", False, "OPENAI_API_KEY not set or too short")
            print("   The agent will fall back to stub AI")
            return False
    except Exception as e:
        print_test("OpenAI Config", False, f"Error: {str(e)}")
        return False

def main():
    """Run all diagnostic tests."""
    print("=" * 60)
    print("CHAT ENDPOINT DIAGNOSTIC TOOL")
    print("=" * 60)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Test user ID: {TEST_USER_ID}")
    print("=" * 60)

    # Run tests
    results = []

    results.append(("Backend Running", test_backend_running()))
    results.append(("Chat Endpoint Exists", test_chat_endpoint_exists()))
    results.append(("OpenAI Config", test_openai_config()))
    results.append(("Chat With Auth", test_chat_with_auth()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Chat endpoint should be working.")
        print("\nNext steps:")
        print("1. Make sure you're logged in on the frontend")
        print("2. Check browser console for any errors")
        print("3. Verify the frontend is using the correct user ID from auth context")
    else:
        print("\n[ERROR] Some tests failed. Check the issues above.")
        print("\nCommon fixes:")
        print("- Make sure backend is running: python backend/run_server.py")
        print("- Check OPENAI_API_KEY in backend/.env")
        print("- Verify JWT_SECRET_KEY matches in backend/.env")
        print("- Make sure user exists in database (create account on frontend)")

if __name__ == "__main__":
    main()
