#!/usr/bin/env python
"""
Minimal test for LangGraph state functionality
"""

from __future__ import print_function
import sys
import copy

print("Python version:", sys.version)

# Define a simple employee class
class Employee(object):
    def __init__(self, name, position):
        self.name = name
        self.position = position

# Create a state dictionary
state = {
    "employee": Employee("John Doe", "Developer"),
    "notes": []
}

print("Initial state keys:", state.keys())
print("Employee name:", state["employee"].name)

# Create a copy of state and modify it
def modify_state(state):
    # Create a DEEP copy
    new_state = copy.deepcopy(state)
    # Update notes
    notes = new_state.get("notes", [])
    notes.append("Note added")
    new_state["notes"] = notes
    return new_state

# Apply the modification
new_state = modify_state(state)

print("Modified state notes count:", len(new_state["notes"]))
print("Original state notes count:", len(state["notes"]))

print("Test completed successfully!") 