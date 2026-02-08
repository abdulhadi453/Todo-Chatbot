#!/usr/bin/env python3
"""
Test Runner Script for Todo Backend API with Authentication

This script runs the complete test suite for the authentication feature.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the complete test suite"""
    print("Running complete test suite for Todo Backend API with Authentication...")

    # We're already in the backend directory, so no need to change
    # Just make sure we're in the right place
    current_dir = os.getcwd()
    if not os.path.exists("tests"):
        # If tests directory doesn't exist here, try to find it
        raise FileNotFoundError("tests directory not found in current location")

    # Run all tests
    test_commands = [
        ["python", "-m", "pytest", "tests/auth/", "-v"],
        ["python", "-m", "pytest", "tests/integration/", "-v"],
        ["python", "-m", "pytest", "tests/", "-v"]
    ]

    for i, cmd in enumerate(test_commands):
        print(f"\n--- Running test group {i+1}/{len(test_commands)} ---")
        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True)
            print(f"✓ Test group {i+1} completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"X Test group {i+1} failed with return code {e.returncode}")
            return False

    print("\n🎉 All tests completed successfully!")
    print("Full functionality verification passed.")
    return True


def main():
    """Main function to run tests"""
    print("Todo Backend API - Authentication Test Suite")
    print("=" * 50)

    success = run_tests()

    if not success:
        print("\nX Some tests failed. Please check the output above.")
        sys.exit(1)
    else:
        print("\nV All tests passed! The authentication system is working correctly.")


if __name__ == "__main__":
    main()