#!/usr/bin/env python
"""
Simple test script to verify basic functionality
Works with both Python 2.x and 3.x
"""

from __future__ import print_function
import sys
import os

print("Python version:", sys.version)

# Test creating a simple employee object
class Employee(object):
    def __init__(self, name, position):
        self.name = name
        self.position = position

try:
    # Create an employee
    employee = Employee("Test User", "Tester")
    print("Created employee: {} - {}".format(employee.name, employee.position))
    
    # Create a state dictionary
    state = {"employee": employee, "notes": []}
    print("State keys:", state.keys())
    print("Employee in state:", state["employee"].name)
    
    # Create a copy of the state
    new_state = state.copy()
    print("New state keys:", new_state.keys())
    print("Employee in new state:", new_state["employee"].name)
    
    print("\nBasic functionality test passed!")

except Exception as e:
    print("Error during test:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nNow testing Groq API")
try:
    # Try to import and use langchain
    from langchain_groq import ChatGroq
    
    # Check if the API key is set
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY is not set. Setting it from the script...")
        os.environ["GROQ_API_KEY"] = "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"
    
    # Test creating an LLM
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
    print("Initialized ChatGroq successfully")
    
    print("\nGroq API test passed!")
    
except ImportError as e:
    print("ImportError: {}".format(e))
    print("Make sure to install the required packages:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print("Error testing Groq API:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed successfully!") 