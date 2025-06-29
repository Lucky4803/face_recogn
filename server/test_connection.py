#!/usr/bin/env python3
"""
Test script to verify all connections and dependencies
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing Python imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("✅ face_recognition imported successfully")
    except ImportError as e:
        print(f"❌ face_recognition import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from supabase import create_client
        print("✅ Supabase client imported successfully")
    except ImportError as e:
        print(f"❌ Supabase import failed: {e}")
        return False
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print("✅ Google Sheets libraries imported successfully")
    except ImportError as e:
        print(f"❌ Google Sheets libraries import failed: {e}")
        return False
    
    return True

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🔗 Testing Supabase connection...")
    
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in .env file")
        print("📝 Please update server/.env with your Supabase service role key")
        return False
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to fetch from students table
        response = supabase.table('students').select('count').execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_camera():
    """Test camera access"""
    print("\n📷 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Cannot read from camera")
            cap.release()
            return False
        
        print(f"✅ Camera working - Frame size: {frame.shape}")
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets connection"""
    print("\n📊 Testing Google Sheets connection...")
    
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json not found - Google Sheets integration will not work")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        import gspread
        
        credentials = Credentials.from_service_account_file('credentials.json')
        gc = gspread.authorize(credentials)
        
        # Test by listing spreadsheets (this will fail if credentials are invalid)
        spreadsheets = gc.openall()
        print(f"✅ Google Sheets connection successful - Found {len(spreadsheets)} spreadsheets")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 Face Recognition System - Connection Test")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test Supabase
    if not test_supabase_connection():
        all_tests_passed = False
    
    # Test camera
    if not test_camera():
        all_tests_passed = False
    
    # Test Google Sheets
    if not test_google_sheets():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return all_tests_passed

if __name__ == "__main__":
    main()