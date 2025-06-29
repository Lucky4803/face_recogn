#!/usr/bin/env python3
"""
Setup script for the Face Recognition Server
This script helps set up the Python environment and dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def check_camera():
    """Check if camera is available"""
    print("Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera is available")
            cap.release()
            return True
        else:
            print("✗ Camera is not available")
            return False
    except ImportError:
        print("✗ OpenCV not installed")
        return False

def setup_environment():
    """Set up environment variables"""
    print("Setting up environment...")
    
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        with open('.env.example', 'r') as template:
            with open('.env', 'w') as env_file:
                env_file.write(template.read())
        print("✓ .env file created. Please update it with your credentials.")
    else:
        print("✓ .env file already exists")

def main():
    print("=== Face Recognition Server Setup ===")
    print()
    
    # Install requirements
    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        return False
    
    # Check camera
    check_camera()
    
    # Setup environment
    setup_environment()
    
    print()
    print("=== Setup Complete ===")
    print("Next steps:")
    print("1. Update the .env file with your Supabase credentials")
    print("2. Add your Google Sheets service account credentials.json file")
    print("3. Run the server with: python app.py")
    print()
    
    return True

if __name__ == "__main__":
    main()