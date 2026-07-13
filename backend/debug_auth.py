#!/usr/bin/env python3
"""
Auth debugging tool to diagnose login issues.
Run this to test password hashing and identify auth problems.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from config.database import engine
from src.models.todo_model import User

def test_password_flow(email: str, test_passwords: list):
    """Test if any of the test passwords work for the user."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            print(f"[ERROR] No user found with email: {email}")
            return False

        print(f"\n[INFO] User found: {user.email}")
        print(f"[INFO] User ID: {user.id}")
        print(f"[INFO] Password hash algorithm: {user.password_hash.split('$')[1] if '$' in user.password_hash else 'unknown'}")

        print("\n[TEST] Testing passwords...")
        for pwd in test_passwords:
            try:
                is_valid = user.verify_password(pwd)
                if is_valid:
                    print(f"  [PASS] Password '{pwd}' works!")
                    return True
                else:
                    print(f"  [FAIL] Password '{pwd}' does not match")
            except Exception as e:
                print(f"  [ERROR] Exception testing '{pwd}': {str(e)}")

        print(f"\n[RESULT] None of the test passwords work")
        return False

def create_test_user(email: str, password: str, name: str = "Test User"):
    """Create a test user with known password."""
    with Session(engine) as session:
        # Check if user already exists
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print(f"[INFO] User {email} already exists. Updating password...")
            # Update password
            existing.password_hash = User.hash_password(password)
            session.add(existing)
            session.commit()
            print(f"[SUCCESS] Password updated for {email}")
            return existing.id
        else:
            # Create new user
            import uuid
            from datetime import datetime, timezone

            new_user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                password_hash=User.hash_password(password),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"[SUCCESS] Created new user: {email} with ID: {new_user.id}")
            return new_user.id

def test_hash_verify_cycle(password: str):
    """Test that hash -> verify cycle works."""
    print(f"\n[TEST] Testing hash/verify cycle with password: '{password}'")

    # Hash the password
    hashed = User.hash_password(password)
    print(f"  Hashed: {hashed[:60]}...")

    # Create a mock user to test verification
    class MockUser:
        def __init__(self, hash_val):
            self.password_hash = hash_val
        def verify_password(self, pwd):
            return User.verify_password(self, pwd)

    mock = MockUser(hashed)

    # Test verification
    is_valid = mock.verify_password(password)
    print(f"  Verification result: {is_valid}")

    if is_valid:
        print("  [PASS] Hash/verify cycle works correctly")
    else:
        print("  [FAIL] Hash/verify cycle is broken!")

    return is_valid

def main():
    print("=" * 70)
    print("AUTH DEBUGGING TOOL")
    print("=" * 70)

    # Test 1: Verify hash/verify cycle works
    print("\n## TEST 1: Hash/Verify Cycle")
    cycle_works = test_hash_verify_cycle("TestPassword123!")

    if not cycle_works:
        print("\n[CRITICAL] Password hashing/verification is broken!")
        print("This needs to be fixed before proceeding.")
        return

    # Test 2: Check existing user
    print("\n## TEST 2: Existing User Login")
    existing_email = "ah6335171@gmail.com"
    common_passwords = [
        "Test123!",
        "test123",
        "Test1234",
        "Password123!",
        "password",
        "123456"
    ]

    works = test_password_flow(existing_email, common_passwords)

    if not works:
        print("\n[INFO] Existing user password unknown.")
        print("[SOLUTION] You have two options:")
        print("  1. Reset password for this user (run with --reset)")
        print("  2. Create a new test account")

    # Test 3: Create/test a known user
    print("\n## TEST 3: Create Test User")
    test_email = "test@example.com"
    test_password = "TestPass123!"

    user_id = create_test_user(test_email, test_password, "Test User")

    # Verify the test user immediately
    print("\n[VERIFY] Testing login with newly created user...")
    works = test_password_flow(test_email, [test_password, "wrong_password"])

    if works:
        print("\n[SUCCESS] Auth system is working correctly!")
        print(f"[INFO] You can login with:")
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
    else:
        print("\n[ERROR] Auth system has issues even with fresh user!")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Hash/Verify cycle: {'WORKING' if cycle_works else 'BROKEN'}")
    print(f"Test user login: {'WORKING' if works else 'BROKEN'}")

    if cycle_works and works:
        print("\n[RECOMMENDATION] Auth system is functional.")
        print("Your existing user password may just be forgotten.")
        print("Option 1: Use the test account (test@example.com / TestPass123!)")
        print("Option 2: Sign up with a new account")
        print("Option 3: Reset password for existing user (feature to be added)")

if __name__ == "__main__":
    main()
