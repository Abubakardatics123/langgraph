#!/usr/bin/env python3
"""
Check the data store to ensure employees are being created properly
"""

import os
import sys
import json

def check_data_dir():
    """Check the data directory and its contents"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the data directory and employees file
    data_dir = os.path.join(current_dir, "data")
    employees_file = os.path.join(data_dir, "employees.json")
    
    print(f"Current directory: {current_dir}")
    print(f"Data directory: {data_dir}")
    print(f"Employees file: {employees_file}")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print("Data directory does not exist! Creating it...")
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    else:
        print("Data directory exists.")
    
    # Check if employees file exists
    if not os.path.exists(employees_file):
        print("Employees file does not exist! Creating sample data...")
        
        # Create sample data
        sample_data = [
            {
                "id": "1682900001",
                "name": "Test User 1",
                "position": "Software Engineer",
                "department": "Engineering",
                "startDate": "2023-05-01",
                "status": "Complete"
            },
            {
                "id": "1682900002",
                "name": "Test User 2",
                "position": "Product Manager",
                "department": "Product",
                "startDate": "2023-06-15",
                "status": "In Progress"
            }
        ]
        
        # Write sample data to file
        with open(employees_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"Created employees file with sample data: {employees_file}")
    else:
        print("Employees file exists.")
        
        # Read the employees file
        try:
            with open(employees_file, "r") as f:
                employees = json.load(f)
            
            print(f"Found {len(employees)} employees in the file:")
            for i, emp in enumerate(employees):
                print(f"  Employee {i+1}: {emp.get('name', 'Unknown')} (ID: {emp.get('id', 'Unknown')})")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading employees file: {e}")
            
            # Backup the corrupted file
            backup_file = f"{employees_file}.backup"
            print(f"Backing up corrupted file to: {backup_file}")
            os.rename(employees_file, backup_file)
            
            # Create a new file with sample data
            print("Creating new file with sample data...")
            sample_data = [
                {
                    "id": "1682900001",
                    "name": "Test User 1",
                    "position": "Software Engineer",
                    "department": "Engineering",
                    "startDate": "2023-05-01",
                    "status": "Complete"
                }
            ]
            
            with open(employees_file, "w") as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"Created new employees file with sample data: {employees_file}")

if __name__ == "__main__":
    check_data_dir() 