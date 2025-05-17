"""
Data access module for Streamlit app
Provides direct access to employee data without requiring the Flask API
"""

import os
import json
from datetime import datetime

# Path to the data directory and files
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")

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
            employees = generate_sample_employees()
            save_employees(employees)
            return employees
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading employees: {e}")
        # If there's an error, return sample data
        employees = generate_sample_employees()
        return employees

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
            "status": "Completed",
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
            "status": "In Progress",
            "equipmentNeeds": ["Laptop", "Phone", "Headset"],
            "systemAccess": ["Email", "CRM", "Sales Tools"],
            "trainingRequirements": ["Sales Training", "CRM Usage"],
            "created_at": "2023-06-25T11:15:00.000Z",
            "updated_at": "2023-06-25T11:15:00.000Z"
        },
        {
            "id": "1682900004",
            "name": "Emily Davis",
            "position": "HR Specialist",
            "department": "HR",
            "startDate": "2023-04-15",
            "status": "Completed",
            "equipmentNeeds": ["Laptop", "Phone"],
            "systemAccess": ["Email", "HR System", "Payroll"],
            "trainingRequirements": ["HR Policies", "Compliance"],
            "created_at": "2023-04-10T08:45:00.000Z",
            "updated_at": "2023-04-10T08:45:00.000Z"
        },
        {
            "id": "1682900005",
            "name": "David Wilson",
            "position": "Marketing Specialist",
            "department": "Marketing",
            "startDate": "2023-08-01",
            "status": "Pending",
            "equipmentNeeds": ["Laptop", "Graphics Tablet"],
            "systemAccess": ["Email", "Marketing Tools", "Social Media"],
            "trainingRequirements": ["Brand Guidelines", "Marketing Systems"],
            "created_at": "2023-07-25T14:20:00.000Z",
            "updated_at": "2023-07-25T14:20:00.000Z"
        }
    ]
    return sample_data

def save_employees(employees):
    """Save employees to the JSON file"""
    ensure_data_dir()
    
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
    employee_id = str(int(datetime.now().timestamp()))
    
    # Add timestamp and ID
    employee_data["id"] = employee_id
    employee_data["created_at"] = datetime.now().isoformat()
    employee_data["updated_at"] = employee_data["created_at"]
    
    # Ensure status field exists
    if "status" not in employee_data:
        employee_data["status"] = "New"
    
    employees.append(employee_data)
    save_employees(employees)
    
    return employee_data 