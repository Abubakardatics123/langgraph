#!/usr/bin/env python
"""
Test script for LangGraph workflow.
This script tests the LangGraph workflow directly, bypassing the API,
to verify that the workflow is functioning correctly.
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import the LangGraph modules
try:
    from hr_langgraph import start_onboarding_workflow, EmployeeInfo
    print("Successfully imported hr_langgraph module")
except ImportError as e:
    print(f"Error importing hr_langgraph: {e}")
    sys.exit(1)

try:
    from langgraph_integration import process_employee_with_langgraph, save_workflow_results
    print("Successfully imported langgraph_integration module")
except ImportError as e:
    print(f"Error importing langgraph_integration: {e}")
    sys.exit(1)

def test_direct_workflow():
    """Test the LangGraph workflow directly."""
    print("\n===== Testing direct workflow =====")
    # Create a sample employee
    sample_employee = EmployeeInfo(
        name="Test User",
        position="Software Developer",
        department="Engineering",
        start_date="2025-06-01",
        employee_id="EMP12345",
        equipment_needs=["Laptop", "Monitor", "Keyboard"],
        system_access=["GitHub", "Jira", "Slack"],
        status="pending"
    )
    
    # Run the workflow
    print("Starting workflow...")
    result = start_onboarding_workflow(sample_employee)
    
    # Print the results
    print("\nWorkflow completed with the following results:")
    print(f"Completed steps: {result['completed_steps']}")
    print(f"Documents prepared: {result['documents_ready']}")
    print(f"Current step: {result['current_step']}")
    
    # Print messages
    print("\nWorkflow Messages:")
    for message in result["messages"]:
        print(f"\n[{message['role']}]: {message['content']}")
    
    # Print memory
    print("\nMemory State:")
    for key, value in result["memory"].items():
        print(f"{key}: {value}")
    
    return result

def test_integration_workflow():
    """Test the integration layer of the workflow."""
    print("\n===== Testing integration workflow =====")
    # Create sample data in the format expected by the API
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
    
    # Process the employee through the integration layer
    print("Starting integration workflow...")
    result = process_employee_with_langgraph(sample_data)
    
    # Print the result
    print("\nIntegration workflow result:")
    print(f"Success: {result['success']}")
    print(f"Completed steps: {result.get('completed_steps', [])}")
    print(f"Status: {result.get('status', 'unknown')}")
    
    # Print messages if available
    if "messages" in result:
        print("\nWorkflow Messages:")
        for message in result["messages"]:
            print(f"\n[{message['role']}]: {message['content']}")
    
    # Print memory if available
    if "memory" in result:
        print("\nMemory State:")
        for key, value in result["memory"].items():
            print(f"{key}: {value}")
    
    return result

def save_test_results(result, test_name):
    """Save test results to a file."""
    # Create directory if it doesn't exist
    os.makedirs("test_results", exist_ok=True)
    
    # Create a filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results/{test_name}_{timestamp}.json"
    
    # Save the file
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nTest results saved to {filename}")
    return filename

if __name__ == "__main__":
    # Run the tests
    print("Starting LangGraph workflow tests")
    
    # Test the direct workflow
    direct_result = test_direct_workflow()
    save_test_results(direct_result, "direct_workflow")
    
    # Test the integration workflow
    integration_result = test_integration_workflow()
    save_test_results(integration_result, "integration_workflow")
    
    print("\nAll tests completed successfully.") 