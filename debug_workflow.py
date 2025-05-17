#!/usr/bin/env python3
"""
Debug script for HR Onboarding Workflow

This script helps diagnose issues with the workflow state handling.
"""

import os
import sys
import copy
import traceback

try:
    print("Python version:", sys.version)
    print("Importing modules...")
    from hr_onboarding_workflow import EmployeeInfo, build_workflow
    
    # Make sure Groq API key is set
    os.environ["GROQ_API_KEY"] = "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"
    
    print("Building workflow...")
    workflow = build_workflow()
    
    print("Creating employee...")
    employee = EmployeeInfo(
        name="Debug Test",
        position="QA Engineer",
        department="Engineering",
        start_date="2023-12-01"
    )
    
    print("Creating state dictionary...")
    state = {
        "employee": employee,
        "hr_notes": [],
        "it_notes": [],
        "messages": []
    }
    
    print("State keys:", state.keys())
    print("Employee in state:", "Yes" if "employee" in state else "No")
    if "employee" in state:
        print("Employee name:", state["employee"].name)
    
    print("\nRunning individual nodes to test...")
    print("\n=== Node 1: collect_employee_info ===")
    try:
        from hr_onboarding_workflow import collect_employee_info
        node1_result = collect_employee_info(state)
        print("Node 1 successful!")
        print("Result has these keys:", node1_result.keys())
    except Exception as e:
        print("Node 1 failed:", type(e).__name__, "-", str(e))
        traceback.print_exc()
    
    print("\n=== Running full workflow ===")
    try:
        fresh_state = {
            "employee": employee,
            "hr_notes": [],
            "it_notes": [],
            "messages": []
        }
        
        # Shallow copy of state for debugging
        print("Keys in fresh_state:", fresh_state.keys())
        print("Type of fresh_state:", type(fresh_state))
        
        # Convert to dict if needed (in case it's a special state object)
        if hasattr(fresh_state, "to_dict"):
            invoke_state = fresh_state.to_dict()
        else:
            invoke_state = dict(fresh_state)
            
        print("Running workflow with state dict...")
        result = workflow.invoke(invoke_state)
        
        print("Workflow completed successfully!")
        print("Result keys:", result.keys())
        
        # Print some results
        if "employee" in result:
            emp = result["employee"]
            print("\nResult summary:")
            print(f"Equipment: {len(emp.equipment_needs)} items")
            print(f"Access: {len(emp.system_access)} systems")
            print(f"Training: {len(emp.training_requirements)} courses")
            print(f"Status: {emp.onboarding_status}")
    
    except Exception as e:
        print("Workflow failed:", type(e).__name__, "-", str(e))
        traceback.print_exc()

except Exception as e:
    print("Setup error:", type(e).__name__, "-", str(e))
    traceback.print_exc() 