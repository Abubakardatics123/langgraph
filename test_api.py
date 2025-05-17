#!/usr/bin/env python3
"""
Test script to diagnose API errors in the HR workflow
"""

import json
import sys
import traceback

try:
    print("Testing direct workflow invocation...")
    from hr_onboarding_workflow import EmployeeInfo, build_workflow
    
    # Build the workflow
    workflow = build_workflow()
    print("Workflow built successfully")
    
    # Create a test employee
    employee = EmployeeInfo(
        name="Test User",
        position="Software Developer",
        department="Engineering",
        start_date="2023-12-01"
    )
    
    # Initialize the state
    initial_state = {
        "employee": employee,
        "hr_notes": [],
        "it_notes": [],
        "messages": []
    }
    
    # Run the workflow
    print("Running workflow...")
    result = workflow.invoke(initial_state)
    print("Workflow completed!")
    
    # Check result keys
    print("Result keys:", ", ".join(result.keys()))
    print("Employee in result:", "Yes" if "employee" in result else "No")
    if "employee" in result:
        print("Employee name:", result["employee"].name)
        print("Equipment needs count:", len(result["employee"].equipment_needs))
        print("Training requirements count:", len(result["employee"].training_requirements))
    
    print("\nTest completed successfully!")

except Exception as e:
    print("ERROR:", type(e).__name__, "-", str(e))
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1) 