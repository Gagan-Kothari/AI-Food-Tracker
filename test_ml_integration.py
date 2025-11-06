#!/usr/bin/env python3
"""
Test script to verify ML model integration and API endpoints
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = 1  # Adjust based on your test user

def test_grocery_suggestions():
    """Test grocery suggestions endpoint"""
    print("Testing grocery suggestions endpoint...")
    
    try:
        response = requests.post(f"{BASE_URL}/user/grocery-suggestions", 
                               json={"userid": TEST_USER_ID})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Grocery suggestions successful: {data.get('count', 0)} suggestions")
            if data.get('suggestions'):
                print("Sample suggestions:")
                for suggestion in data['suggestions'][:3]:
                    print(f"  - {suggestion['name']} ({suggestion['category']}) - {suggestion['priority']} priority")
        else:
            print(f"❌ Grocery suggestions failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Grocery suggestions error: {e}")

def test_recipe_suggestions():
    """Test recipe suggestions endpoint"""
    print("\nTesting recipe suggestions endpoint...")
    
    try:
        # Test with some common ingredients
        test_ingredients = ["chicken", "rice", "tomatoes", "onions", "garlic"]
        
        response = requests.post(f"{BASE_URL}/user/recipe/suggestions", 
                               json={"ingredients": test_ingredients})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                recipes = data.get('recipes', [])
                print(f"✅ Recipe suggestions successful: {len(recipes)} recipes found")
                if recipes:
                    print("Sample recipes:")
                    for recipe in recipes[:2]:
                        print(f"  - {recipe.get('title', 'Unknown')}")
            else:
                print(f"❌ Recipe suggestions failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Recipe suggestions failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Recipe suggestions error: {e}")

def test_model_training():
    """Test model training endpoint"""
    print("\nTesting model training endpoint...")
    
    try:
        response = requests.post(f"{BASE_URL}/admin/train-models")
        
        if response.status_code == 200:
            data = response.json()
            training_status = data.get('training_status', {})
            print(f"✅ Model training successful: {len(training_status)} users processed")
            
            for user_id, status in list(training_status.items())[:3]:
                print(f"  - User {user_id}: {status}")
        else:
            print(f"❌ Model training failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Model training error: {e}")

def test_inventory():
    """Test inventory endpoint"""
    print("\nTesting inventory endpoint...")
    
    try:
        response = requests.post(f"{BASE_URL}/user/inventory", 
                               json={"userid": TEST_USER_ID})
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Inventory successful: {len(data)} items found")
                if data:
                    print("Sample inventory items:")
                    for item in data[:3]:
                        print(f"  - {item.get('f_name', 'Unknown')} ({item.get('category', 'Unknown category')})")
            else:
                print(f"❌ Inventory failed: Unexpected response format")
        else:
            print(f"❌ Inventory failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Inventory error: {e}")

if __name__ == "__main__":
    print("🧪 Testing ML Integration and API Endpoints")
    print("=" * 50)
    
    # Test basic inventory first
    test_inventory()
    
    # Test model training
    test_model_training()
    
    # Test grocery suggestions
    test_grocery_suggestions()
    
    # Test recipe suggestions
    test_recipe_suggestions()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
