"""
Test script for the update endpoints.

This script tests both the user update and content update endpoints.
Run this after starting the server: uvicorn src.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_update():
    """Test user update endpoint"""
    print("\n" + "="*60)
    print("TESTING USER UPDATE ENDPOINT")
    print("="*60)
    
    # First, create a user
    print("\n1. Creating test user...")
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone_number": "+234801234567",
        "country": "Nigeria",
        "state": "Lagos"
    }
    response = requests.post(f"{BASE_URL}/api/v1/signup", json=signup_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user["id"]
        print(f"✅ User created with ID: {user_id}")
        print(f"   Name: {user['name']}")
        print(f"   Email: {user['email']}")
    else:
        print(f"❌ Failed to create user: {response.json()}")
        return
    
    # Test 1: Update name only
    print("\n2. Updating name only...")
    update_data = {"name": "Updated Test User"}
    response = requests.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data)
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ Name updated successfully")
        print(f"   New name: {updated_user['name']}")
    else:
        print(f"❌ Update failed: {response.json()}")
    
    # Test 2: Update email and phone
    print("\n3. Updating email and phone...")
    update_data = {
        "email": "updated@example.com",
        "phone_number": "+234809876543"
    }
    response = requests.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data)
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ Email and phone updated successfully")
        print(f"   New email: {updated_user['email']}")
        print(f"   New phone: {updated_user['phone_number']}")
    else:
        print(f"❌ Update failed: {response.json()}")
    
    # Test 3: Try to update with invalid name (numbers only)
    print("\n4. Testing validation (name with numbers only)...")
    update_data = {"name": "12345"}
    response = requests.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data)
    if response.status_code == 422:
        print(f"✅ Validation working correctly - rejected invalid name")
    else:
        print(f"❌ Validation failed: {response.status_code}")
    
    # Test 4: Try to update non-existent user
    print("\n5. Testing 404 for non-existent user...")
    response = requests.put(f"{BASE_URL}/api/v1/users/99999", json={"name": "Test"})
    if response.status_code == 404:
        print(f"✅ 404 returned correctly for non-existent user")
    else:
        print(f"❌ Expected 404, got: {response.status_code}")
    
    return user_id


def test_content_update(user_id):
    """Test content update endpoint"""
    print("\n" + "="*60)
    print("TESTING CONTENT UPDATE ENDPOINT")
    print("="*60)
    
    # First, create content
    print("\n1. Creating test content...")
    content_data = {
        "title": "Test Content",
        "image": "/path/to/image.jpg",
        "content": "This is test content",
        "user_id": user_id
    }
    response = requests.post(f"{BASE_URL}/api/v1/post-content", json=content_data)
    if response.status_code == 201:
        content = response.json()
        content_id = content["id"]
        print(f"✅ Content created with ID: {content_id}")
        print(f"   Image: {content['image']}")
        print(f"   Content: {content['content']}")
    else:
        print(f"❌ Failed to create content: {response.json()}")
        return
    
    # Test 1: Update image only
    print("\n2. Updating image only...")
    update_data = {"image": "/path/to/new/image.jpg"}
    response = requests.put(f"{BASE_URL}/api/v1/content/{content_id}", json=update_data)
    if response.status_code == 200:
        updated_content = response.json()
        print(f"✅ Image updated successfully")
        print(f"   New image: {updated_content['image']}")
    else:
        print(f"❌ Update failed: {response.json()}")
    
    # Test 2: Update content text only
    print("\n3. Updating content text only...")
    update_data = {"content": "This is updated content text"}
    response = requests.put(f"{BASE_URL}/api/v1/content/{content_id}", json=update_data)
    if response.status_code == 200:
        updated_content = response.json()
        print(f"✅ Content text updated successfully")
        print(f"   New content: {updated_content['content']}")
    else:
        print(f"❌ Update failed: {response.json()}")
    
    # Test 3: Update both image and content
    print("\n4. Updating both image and content...")
    update_data = {
        "image": "/path/to/final/image.jpg",
        "content": "This is the final content"
    }
    response = requests.put(f"{BASE_URL}/api/v1/content/{content_id}", json=update_data)
    if response.status_code == 200:
        updated_content = response.json()
        print(f"✅ Both fields updated successfully")
        print(f"   New image: {updated_content['image']}")
        print(f"   New content: {updated_content['content']}")
    else:
        print(f"❌ Update failed: {response.json()}")
    
    # Test 4: Try to update non-existent content
    print("\n5. Testing 404 for non-existent content...")
    response = requests.put(f"{BASE_URL}/api/v1/content/99999", json={"content": "Test"})
    if response.status_code == 404:
        print(f"✅ 404 returned correctly for non-existent content")
    else:
        print(f"❌ Expected 404, got: {response.status_code}")


def main():
    print("\n" + "="*60)
    print("UPDATE ENDPOINTS TEST SUITE")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  uvicorn src.main:app --reload")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Test server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            return
        print("✅ Server is running\n")
        
        # Run tests
        user_id = test_user_update()
        if user_id:
            test_content_update(user_id)
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Make sure it's running:")
        print("   uvicorn src.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
