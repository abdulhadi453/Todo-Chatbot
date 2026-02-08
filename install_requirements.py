#!/usr/bin/env python3
"""
Requirements Installer Script

This script installs all required Python packages for the Todo Backend API.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages from requirements.txt"""
    requirements_file = "backend/requirements.txt"

    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found!")
        return False

    print(f"Installing packages from {requirements_file}...")

    try:
        # Read requirements file to show what will be installed
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

        print("Packages to install:")
        for pkg in packages:
            print(f"  - {pkg}")

        # Install packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True, capture_output=True, text=True)

        print("Installation completed successfully!")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def check_installed_packages():
    """Check if required packages are installed"""
    try:
        import fastapi
        import sqlmodel
        import uvicorn
        import pytest
        import httpx
        print("All required packages are installed!")
        return True
    except ImportError as e:
        print(f"Missing package: {e.name if hasattr(e, 'name') else e}")
        return False

def main():
    """Main function to handle installation"""
    print("Todo Backend API - Requirements Installation")
    print("=" * 50)

    # Check if packages are already installed
    if check_installed_packages():
        print("All required packages are already installed.")
        return

    print("\nInstalling missing packages...")

    # Install requirements
    if install_requirements():
        print("\nVerification after installation:")
        if check_installed_packages():
            print("\n✓ All packages installed successfully!")
        else:
            print("\n✗ Some packages may not have installed correctly.")
    else:
        print("\n✗ Package installation failed.")

if __name__ == "__main__":
    main()