import os
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Import the LangGraph workflow
# Ensure correct import path
try:
    from hr_langgraph import start_onboarding_workflow, EmployeeInfo
except ImportError:
    # Try adding current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from hr_langgraph import start_onboarding_workflow, EmployeeInfo
    except ImportError:
        print("ERROR: Could not import hr_langgraph module. Make sure it exists in the same directory.")
        raise

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
    
    # If no equipment was selected, add default laptop
    if not equipment_needs:
        equipment_needs = ["Laptop"]
    
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
    
    # If no access was selected, add default email
    if not system_access:
        system_access = ["Email"]
    
    # Format date
    start_date = employee_data.get('startDate', datetime.now().strftime("%Y-%m-%d"))
    
    # Generate an employee ID if not present
    emp_id = employee_data.get('id', f"EMP{hash(employee_data.get('name', '')) % 10000}")
    
    print(f"Converting employee data for {employee_data.get('name', '')}")
    print(f"Equipment needs: {equipment_needs}")
    print(f"System access: {system_access}")
    
    # Create the employee info object
    return EmployeeInfo(
        name=employee_data.get('name', ''),
        position=employee_data.get('position', ''),
        department=employee_data.get('department', ''),
        start_date=start_date,
        employee_id=emp_id,
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
        print(f"Starting LangGraph workflow processing for {employee_data.get('name', '')}")
        
        # Convert to LangGraph format
        langgraph_employee = convert_to_langgraph_format(employee_data)
        
        # Run the workflow
        print("Executing workflow...")
        result = start_onboarding_workflow(langgraph_employee)
        print(f"Workflow execution completed for {langgraph_employee['name']}")
        
        # Extract memory for additional context
        memory = result.get("memory", {})
        timestamps = {
            "documents_generated_at": memory.get("documents_generated_at", "unknown"),
            "welcome_message_generated_at": memory.get("welcome_message_generated_at", "unknown"),
            "equipment_provisioned_at": memory.get("equipment_provisioned_at", "unknown")
        }
        
        # Return a simplified result with memory data
        return {
            "success": True,
            "employee_name": langgraph_employee["name"],
            "completed_steps": result["completed_steps"],
            "documents": result["documents_ready"],
            "messages": result["messages"],
            "status": "processed",
            "memory": memory,
            "timestamps": timestamps
        }
    except Exception as e:
        print(f"Error in process_employee_with_langgraph: {str(e)}")
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
    print("Testing LangGraph workflow with sample data")
    result = process_employee_with_langgraph(sample_data)
    
    # Print the result
    print("Workflow result:")
    print(json.dumps(result, indent=2)) 