#!/usr/bin/env python3
"""
Fixed Workflow Integration for HR Onboarding

This script replaces the LangGraph integration with the simplified workflow.
"""

import os
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Import the simplified workflow
try:
    from simplified_workflow import process_onboarding
    print("Successfully imported simplified_workflow module")
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from simplified_workflow import process_onboarding
        print("Successfully imported simplified_workflow module (after path adjustment)")
    except ImportError:
        print("ERROR: Could not import simplified_workflow module.")
        print("Make sure it exists in the same directory.")
        raise

# Function to process an employee through the simplified workflow
def process_employee(employee_data: Dict) -> Dict:
    """
    Process an employee through the simplified workflow and return the result
    """
    try:
        print(f"Starting simplified workflow processing for {employee_data.get('name', '')}")
        
        # Run the workflow
        print("Executing workflow...")
        result = process_onboarding(employee_data)
        print(f"Workflow execution completed for {employee_data.get('name', '')}")
        
        # Format the result to match what the frontend expects
        return {
            "success": True,
            "employee": {
                "name": employee_data.get('name', ''),
                "position": employee_data.get('position', ''),
                "department": employee_data.get('department', ''),
                "startDate": employee_data.get('startDate', ''),
                "equipmentNeeds": result.get("employee", {}).get("equipmentNeeds", []),
                "systemAccess": result.get("employee", {}).get("systemAccess", []),
                "trainingRequirements": result.get("employee", {}).get("trainingRequirements", []),
                "status": "completed"
            },
            "hrNotes": result.get("hrNotes", []),
            "itNotes": result.get("itNotes", []),
            "completed_steps": ["employee_info", "equipment_access", "training_plan"],
            "documents": ["Welcome Letter", "Equipment Request Form", "Access Request Form", "Training Plan"],
        }
    except Exception as e:
        print(f"Error in process_employee: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "employee_name": employee_data.get('name', ''),
            "status": "failed"
        }

# Function to save workflow results to a file
def save_workflow_results(result: Dict, employee_id: str) -> str:
    """
    Save workflow results to a JSON file and return the file path
    """
    # Create directory if it doesn't exist
    os.makedirs("data/workflows", exist_ok=True)
    
    # Create a filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/workflows/workflow_{employee_id}_{timestamp}.json"
    
    # Save the file
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Saved workflow results to {filename}")
    return filename

# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "name": "Jane Smith",
        "position": "Product Manager",
        "department": "Product",
        "startDate": "2025-07-01",
        "equipment": {
            "laptop": True,
            "monitor": True,
            "keyboard": True,
            "mouse": True,
            "headset": True
        },
        "access": {
            "email": True,
            "github": True,
            "slack": True,
            "jira": True,
            "drive": True
        }
    }
    
    # Process the employee
    print("Testing simplified workflow with sample data")
    result = process_employee(sample_data)
    
    # Print the result
    print("Workflow result:")
    print(json.dumps(result, indent=2)) 