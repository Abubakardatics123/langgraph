#!/usr/bin/env python3
"""
Fix employee status values in the data store
"""

import os
import sys
import json

def fix_employee_statuses():
    """Check and fix status values for all employees"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the data file path
    data_dir = os.path.join(current_dir, "data")
    employees_file = os.path.join(data_dir, "employees.json")
    
    print(f"Checking employee data in: {employees_file}")
    
    # Check if file exists
    if not os.path.exists(employees_file):
        print("Employees file doesn't exist. Nothing to fix.")
        return
    
    # Read the current data
    try:
        with open(employees_file, "r") as f:
            employees = json.load(f)
        
        if not employees:
            print("No employees found in the data file.")
            return
        
        print(f"Found {len(employees)} employees.")
        
        # Map of status values before fixing
        status_before = {}
        for emp in employees:
            status = emp.get("status")
            status_before[status] = status_before.get(status, 0) + 1
        
        print("Status values before fixing:")
        for status, count in status_before.items():
            print(f"  {status if status else 'None'}: {count}")
        
        # Fix status values
        fixed_count = 0
        for emp in employees:
            # Initialize status if missing
            if "status" not in emp or emp["status"] is None:
                emp["status"] = "New"
                fixed_count += 1
                continue
            
            status = emp["status"].lower()
            
            # Fix common status values
            if status in ["complete", "completed", "done"]:
                emp["status"] = "Completed"
                fixed_count += 1
            elif status in ["in progress", "inprogress", "in-progress"]:
                emp["status"] = "In Progress"
                fixed_count += 1
            elif status in ["pending", "new", "waiting"]:
                emp["status"] = "Pending"
                fixed_count += 1
        
        # Map of status values after fixing
        status_after = {}
        for emp in employees:
            status = emp.get("status")
            status_after[status] = status_after.get(status, 0) + 1
        
        print("\nStatus values after fixing:")
        for status, count in status_after.items():
            print(f"  {status if status else 'None'}: {count}")
        
        # Save the updated data
        if fixed_count > 0:
            with open(employees_file, "w") as f:
                json.dump(employees, f, indent=2)
            print(f"\nFixed {fixed_count} status values and saved the file.")
        else:
            print("\nNo status values needed fixing.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_employee_statuses() 