import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# Import the LangGraph workflow
from hr_langgraph import start_onboarding_workflow, EmployeeInfo

# Function to convert Flask employee data to LangGraph format
def convert_to_langgraph_format(employee_data: Dict) -> EmployeeInfo:
    """
    Convert employee data from Flask API format to LangGraph format
    """
    # Extract equipment needs and system access from the data
    equipment_needs = []
    if employee_data.get('equipment', {}).get('laptop', False):
        equipment_needs.append("Laptop")
    if employee_data.get('equipment', {}).get('monitor', False):
        equipment_needs.append("Monitor")
    if employee_data.get('equipment', {}).get('keyboard', False):
        equipment_needs.append("Keyboard")
    if employee_data.get('equipment', {}).get('mouse', False):
        equipment_needs.append("Mouse")
    if employee_data.get('equipment', {}).get('headset', False):
        equipment_needs.append("Headset")
    
    system_access = []
    if employee_data.get('access', {}).get('email', False):
        system_access.append("Email")
    if employee_data.get('access', {}).get('github', False):
        system_access.append("GitHub")
    if employee_data.get('access', {}).get('slack', False):
        system_access.append("Slack")
    if employee_data.get('access', {}).get('jira', False):
        system_access.append("Jira")
    if employee_data.get('access', {}).get('drive', False):
        system_access.append("Google Drive")
    
    # Format date
    start_date = employee_data.get('startDate', datetime.now().strftime("%Y-%m-%d"))
    
    # Create the employee info object
    return EmployeeInfo(
        name=employee_data.get('name', ''),
        position=employee_data.get('position', ''),
        department=employee_data.get('department', ''),
        start_date=start_date,
        employee_id=employee_data.get('id', f"EMP{hash(employee_data.get('name', '')) % 10000}"),
        equipment_needs=equipment_needs,
        system_access=system_access,
        status="pending"
    )

# Function to process an employee through the LangGraph workflow
def process_employee_with_langgraph(employee_data: Dict) -> Dict:
    """
    Process an employee through the LangGraph workflow and return the result
    """
    try:
        # Convert to LangGraph format
        langgraph_employee = convert_to_langgraph_format(employee_data)
        
        # Run the workflow
        result = start_onboarding_workflow(langgraph_employee)
        
        # Return a simplified result
        return {
            "success": True,
            "employee_name": langgraph_employee["name"],
            "completed_steps": result["completed_steps"],
            "documents": result["documents_ready"],
            "messages": result["messages"],
            "status": "processed"
        }
    except Exception as e:
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
    result = process_employee_with_langgraph(sample_data)
    
    # Print the result
    print(json.dumps(result, indent=2)) 