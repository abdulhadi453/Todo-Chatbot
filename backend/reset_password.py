#!/usr/bin/env python3
"""
Password reset utility for existing users.
Usage: python reset_password.py <email> <new_password>
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from config.database import engine
from src.models.todo_model import User

def reset_password(email: str, new_password: str):
    """Reset password for an existing user."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            print(f"[ERROR] No user found with email: {email}")
            return False

        # Update password
        user.password_hash = User.hash_password(new_password)
        session.add(user)
        session.commit()

        print(f"[SUCCESS] Password updated for {email}")
        print(f"[INFO] User ID: {user.id}")

        # Verify the new password works
        user_check = session.exec(select(User).where(User.email == email)).first()
        if user_check and user_check.verify_password(new_password):
            print(f"[VERIFIED] New password works correctly!")
            return True
        else:
            print(f"[WARNING] Password may not have been set correctly")
            return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("\nExample:")
        print("  python reset_password.py user@example.com NewPass123!")
        sys.exit(1)

    email = sys.argv[1]
    new_password = sys.argv[2]

    print("=" * 60)
    print("PASSWORD RESET UTILITY")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"New Password: {'*' * len(new_password)}")
    print()

    success = reset_password(email, new_password)

    if success:
        print("\n[DONE] You can now login with:")
        print(f"  Email: {email}")
        print(f"  Password: {new_password}")
    else:
        print("\n[FAILED] Could not reset password")

if __name__ == "__main__":
    main()
