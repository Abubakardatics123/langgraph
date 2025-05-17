#!/usr/bin/env python3
"""
Simple script to test the employees API endpoint directly
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:5001"

def test_employees_api():
    """Test the employees API endpoint"""
    
    print("=== Testing Employees API ===\n")
    
    # 1. Login first
    print("1. Logging in...")
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/admin/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.ok:
        print("Login successful!")
    else:
        print(f"Login failed: {login_response.text}")
        return
    
    # Get cookies from login response
    cookies = login_response.cookies
    print(f"Cookies received: {cookies.get_dict()}")
    
    # 2. Check auth with cookies
    print("\n2. Checking authentication...")
    auth_response = requests.get(
        f"{BASE_URL}/api/admin/check-auth",
        cookies=cookies
    )
    
    print(f"Auth check status: {auth_response.status_code}")
    if auth_response.ok:
        print(f"Auth check successful: {auth_response.json()}")
    else:
        print(f"Auth check failed: {auth_response.text}")
    
    # 3. Get employees
    print("\n3. Fetching employees...")
    employees_response = requests.get(
        f"{BASE_URL}/api/admin/employees",
        cookies=cookies,
        headers={"Accept": "application/json"}
    )
    
    print(f"Employees API status: {employees_response.status_code}")
    
    if employees_response.ok:
        data = employees_response.json()
        employees = data.get("employees", [])
        print(f"Successfully retrieved {len(employees)} employees")
        
        # Print first few employees
        for i, emp in enumerate(employees[:3]):
            print(f"  Employee {i+1}: {emp.get('name')} ({emp.get('position')})")
    else:
        print(f"Failed to get employees: {employees_response.text}")

if __name__ == "__main__":
    test_employees_api() 