#!/usr/bin/env python3
"""
Data Store for HR Workflow

This module provides functionality to store and retrieve employee data using JSON files.
"""

import os
import json
import time
import threading
from datetime import datetime

# Path to the data directory and files
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
LOCK = threading.Lock()  # Used to prevent race conditions when multiple writes happen

def ensure_data_dir():
    """Ensure that the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory: {DATA_DIR}")

def load_employees():
    """Load employees from the JSON file"""
    ensure_data_dir()
    
    try:
        if os.path.exists(EMPLOYEES_FILE):
            with open(EMPLOYEES_FILE, 'r') as f:
                employees = json.load(f)
                print(f"Loaded {len(employees)} employees from {EMPLOYEES_FILE}")
                return employees
        else:
            # Create an empty employees file
            print(f"Employees file not found: {EMPLOYEES_FILE}")
            create_sample_data = True
            employees = []
            if create_sample_data:
                print("Creating sample employee data")
                employees = generate_sample_employees()
            save_employees(employees)
            return employees
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading employees: {e}")
        # If there's an error, backup the file and return empty list
        if os.path.exists(EMPLOYEES_FILE):
            backup_file = f"{EMPLOYEES_FILE}.{int(time.time())}.bak"
            os.rename(EMPLOYEES_FILE, backup_file)
            print(f"Corrupted file backed up to {backup_file}")
        return []

def generate_sample_employees():
    """Generate sample employee data"""
    sample_data = [
        {
            "id": "1682900001",
            "name": "John Doe",
            "position": "Software Engineer",
            "department": "Engineering",
            "startDate": "2023-05-01",
            "status": "Completed",
            "equipmentNeeds": ["Laptop", "Monitor", "Keyboard"],
            "systemAccess": ["Email", "GitHub", "Jira"],
            "trainingRequirements": ["Security Training", "Code Standards"],
            "created_at": "2023-05-01T09:00:00.000Z",
            "updated_at": "2023-05-01T09:00:00.000Z"
        },
        {
            "id": "1682900002",
            "name": "Jane Smith",
            "position": "Product Manager",
            "department": "Product",
            "startDate": "2023-06-15",
            "status": "In Progress",
            "equipmentNeeds": ["Laptop", "Phone"],
            "systemAccess": ["Email", "Jira", "Analytics"],
            "trainingRequirements": ["Product Management", "Agile Methodologies"],
            "created_at": "2023-06-10T10:30:00.000Z",
            "updated_at": "2023-06-10T10:30:00.000Z"
        },
        {
            "id": "1682900003",
            "name": "Michael Johnson",
            "position": "Sales Representative",
            "department": "Sales",
            "startDate": "2023-07-01",
            "status": "Pending",
            "equipmentNeeds": ["Laptop", "Phone", "Headset"],
            "systemAccess": ["Email", "CRM", "Sales Tools"],
            "trainingRequirements": ["Sales Training", "CRM Usage"],
            "created_at": "2023-06-25T11:15:00.000Z",
            "updated_at": "2023-06-25T11:15:00.000Z"
        }
    ]
    return sample_data

def save_employees(employees):
    """Save employees to the JSON file"""
    ensure_data_dir()
    
    with LOCK:
        try:
            with open(EMPLOYEES_FILE, 'w') as f:
                json.dump(employees, f, indent=2)
            print(f"Saved {len(employees)} employees to {EMPLOYEES_FILE}")
            return True
        except IOError as e:
            print(f"Error saving employees: {e}")
            return False

def add_employee(employee_data):
    """Add a new employee to the storage"""
    employees = load_employees()
    
    # Generate a unique ID
    employee_id = str(int(time.time()))
    
    # Add timestamp and ID
    employee_data["id"] = employee_id
    employee_data["created_at"] = datetime.now().isoformat()
    employee_data["updated_at"] = employee_data["created_at"]
    
    # Ensure status field exists
    if "status" not in employee_data:
        employee_data["status"] = "New"
    
    employees.append(employee_data)
    save_employees(employees)
    print(f"Added new employee: {employee_data['name']} with ID {employee_id}")
    return employee_data

def get_employee(employee_id):
    """Get an employee by ID"""
    employees = load_employees()
    for employee in employees:
        if employee.get("id") == employee_id:
            return employee
    print(f"Employee not found with ID: {employee_id}")
    return None

def update_employee(employee_id, updated_data):
    """Update an existing employee"""
    employees = load_employees()
    
    for i, employee in enumerate(employees):
        if employee.get("id") == employee_id:
            # Preserve id and created_at
            updated_data["id"] = employee_id
            updated_data["created_at"] = employee.get("created_at")
            updated_data["updated_at"] = datetime.now().isoformat()
            
            # Preserve additional fields that may not be in the update
            for key in employee:
                if key not in updated_data and key not in ["id", "created_at", "updated_at"]:
                    updated_data[key] = employee[key]
            
            # Replace the employee in the list
            employees[i] = updated_data
            save_employees(employees)
            print(f"Updated employee with ID: {employee_id}")
            return updated_data
    
    print(f"Failed to update - employee not found with ID: {employee_id}")
    return None  # Employee not found

def delete_employee(employee_id):
    """Delete an employee by ID"""
    employees = load_employees()
    
    for i, employee in enumerate(employees):
        if employee.get("id") == employee_id:
            deleted_employee = employees.pop(i)
            save_employees(employees)
            print(f"Deleted employee: {deleted_employee.get('name')} with ID {employee_id}")
            return True
    
    print(f"Failed to delete - employee not found with ID: {employee_id}")
    return False  # Employee not found

def get_all_employees():
    """Get all employees"""
    employees = load_employees()
    print(f"Returning all {len(employees)} employees")
    return employees

# Initialize data directory on module load
ensure_data_dir() 