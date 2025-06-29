#!/usr/bin/env python3
"""
Enhanced startup script for the Face Recognition Server
Includes dependency checking and better error handling
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install Python requirements with better error handling"""
    print("📦 Installing Python requirements...")
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        print("💡 Try running: pip install --upgrade pip")
        print("💡 Then: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment variables and files"""
    print("🔍 Checking environment setup...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("⚠️  .env file not found, creating from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("📝 Please update .env with your Supabase service role key")
        else:
            print("❌ .env.example not found")
            return False
    
    # Check credentials.json
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json not found")
        print("📝 Google Sheets integration will not work without credentials.json")
    else:
        print("✅ Google Sheets credentials found")
    
    return True

def check_camera():
    """Check if camera is available"""
    print("📷 Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is available")
            cap.release()
            return True
        else:
            print("⚠️  Camera is not available - face recognition will not work")
            return False
    except ImportError:
        print("⚠️  OpenCV not installed - installing now...")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Face Recognition Server...")
    try:
        # Set environment variables
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        # Start the server
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("=" * 50)
    print("🎯 Face Recognition Server Setup & Start")
    print("=" * 50)
    
    # Change to server directory
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check environment
    if not check_environment():
        return False
    
    # Check camera
    check_camera()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete! Starting server...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("=" * 50)
    
    # Wait a moment then start
    time.sleep(2)
    start_server()
    
    return True

if __name__ == "__main__":
    main()