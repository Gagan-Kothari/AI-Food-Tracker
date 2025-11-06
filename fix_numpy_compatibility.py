#!/usr/bin/env python3
"""
Quick fix for numpy compatibility issues
This script resolves the numpy.dtype size mismatch error
"""

import subprocess
import sys
import os

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

def fix_numpy_compatibility():
    """Fix numpy compatibility issues"""
    print("🔧 Fixing numpy compatibility issues...")
    
    # Uninstall existing numpy and pandas
    print("🗑️  Uninstalling existing numpy and pandas...")
    run_command("pip uninstall numpy pandas -y", "Uninstalling numpy and pandas")
    
    # Install compatible versions
    print("📦 Installing compatible versions...")
    
    # Install numpy first
    if not run_command("pip install numpy==1.24.3", "Installing numpy 1.24.3"):
        print("❌ Failed to install numpy")
        return False
    
    # Install pandas
    if not run_command("pip install pandas==2.0.3", "Installing pandas 2.0.3"):
        print("❌ Failed to install pandas")
        return False
    
    # Install other ML dependencies
    if not run_command("pip install xgboost==2.0.3", "Installing xgboost"):
        print("❌ Failed to install xgboost")
        return False
    
    if not run_command("pip install joblib==1.3.2", "Installing joblib"):
        print("❌ Failed to install joblib")
        return False
    
    return True

def test_imports():
    """Test if the fixed libraries can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✅ pandas {pd.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import xgboost as xgb
        print(f"✅ xgboost {xgb.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ xgboost import failed: {e}")
        return False
    
    try:
        import joblib
        print(f"✅ joblib {joblib.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ joblib import failed: {e}")
        return False
    
    return True

def main():
    """Main fix function"""
    print("🚀 Fixing numpy compatibility issues")
    print("=" * 50)
    
    # Fix numpy compatibility
    if not fix_numpy_compatibility():
        print("❌ Failed to fix numpy compatibility")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Numpy compatibility issues fixed!")
    print("\nYou can now run:")
    print("1. python setup_ml_integration.py")
    print("2. python test_ml_integration.py")

if __name__ == "__main__":
    main()
