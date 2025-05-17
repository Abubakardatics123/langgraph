#!/usr/bin/env python3
"""
Debug script to test API endpoints directly
"""

import os
import json
import requests

# API endpoint
BASE_URL = "http://localhost:5001"

def main():
    """Test API endpoints"""
    print("Testing API endpoints...")
    
    # Test health check
    print("\n1. Testing health check endpoint...")
    health_response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {health_response.status_code}")
    print(f"Response: {health_response.json()}")
    
    # Test login
    print("\n2. Testing login endpoint...")
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    login_response = requests.post(
        f"{BASE_URL}/api/admin/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {login_response.status_code}")
    print(f"Response: {login_response.json()}")
    
    # Get the cookies from login response
    cookies = login_response.cookies
    
    # Test auth check
    print("\n3. Testing auth check endpoint...")
    auth_response = requests.get(
        f"{BASE_URL}/api/admin/check-auth",
        cookies=cookies
    )
    print(f"Status: {auth_response.status_code}")
    print(f"Response: {auth_response.json()}")
    
    # Test get employees
    print("\n4. Testing get employees endpoint...")
    employees_response = requests.get(
        f"{BASE_URL}/api/admin/employees",
        cookies=cookies
    )
    print(f"Status: {employees_response.status_code}")
    if employees_response.status_code == 200:
        data = employees_response.json()
        print(f"Found {len(data.get('employees', []))} employees")
        for emp in data.get('employees', [])[:3]:  # Show first 3 employees
            print(f"  - {emp.get('name')} ({emp.get('position')})")
    else:
        print(f"Error: {employees_response.text}")
    
    # Test logout
    print("\n5. Testing logout endpoint...")
    logout_response = requests.post(
        f"{BASE_URL}/api/admin/logout",
        cookies=cookies
    )
    print(f"Status: {logout_response.status_code}")
    print(f"Response: {logout_response.json()}")
    
    # Test auth check after logout
    print("\n6. Testing auth check after logout...")
    auth_after_logout = requests.get(
        f"{BASE_URL}/api/admin/check-auth",
        cookies=cookies
    )
    print(f"Status: {auth_after_logout.status_code}")
    print(f"Response: {auth_after_logout.text}")

if __name__ == "__main__":
    main() 