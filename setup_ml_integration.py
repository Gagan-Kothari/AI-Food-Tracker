#!/usr/bin/env python3
"""
Setup script for ML integration
This script helps set up the ML integration for the AI Food Tracker
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing ML dependencies...")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    # First, upgrade pip and install numpy separately to avoid compatibility issues
    print("🔄 Upgrading pip and installing numpy first...")
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing...")
    
    if not run_command("pip install numpy==1.24.3", "Installing numpy"):
        print("⚠️  Warning: Failed to install specific numpy version, continuing...")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    
    directories = ["aimodels"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")
    
    return True

def test_imports():
    """Test if ML libraries can be imported"""
    print("🧪 Testing ML library imports...")
    
    try:
        import pandas
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import xgboost
        print("✅ xgboost imported successfully")
    except ImportError as e:
        print(f"❌ xgboost import failed: {e}")
        return False
    
    try:
        import joblib
        print("✅ joblib imported successfully")
    except ImportError as e:
        print(f"❌ joblib import failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up ML Integration for AI Food Tracker")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Failed to import ML libraries")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ ML Integration setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("2. Start your frontend: cd frontend2 && npm run dev")
    print("3. Test the integration: python test_ml_integration.py")
    print("4. Check the Admin Tools section in the Dashboard")

if __name__ == "__main__":
    main()
