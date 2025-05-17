#!/usr/bin/env python3
"""
Minimal test to debug LangGraph state issues
"""

import os
import sys
import json
import copy

# Set Groq API key
os.environ["GROQ_API_KEY"] = "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"

# Import LangGraph
try:
    from langgraph.graph import StateGraph, END
    from langchain_groq import ChatGroq
except ImportError:
    print("Required packages not installed.")
    sys.exit(1)

# Create a simple State class
class State(dict):
    """Custom state class for test"""
    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)

# Create a simple Employee class
class Employee:
    def __init__(self, name):
        self.name = name

# Create simple nodes
def node_a(state):
    """First node that simply logs the state"""
    print("Node A received state:", state)
    print("State keys:", state.keys() if state else "Empty")
    print("State type:", type(state))
    
    if not state or "employee" not in state:
        print("Error: Missing employee in state")
        raise KeyError("Missing employee in state")
    
    print("Employee in state:", state["employee"].name)
    
    # Return updated state
    new_state = copy.deepcopy(state)
    new_state["note"] = "Processed by Node A"
    return new_state

def node_b(state):
    """Second node that completes the workflow"""
    print("Node B received state:", state)
    print("State keys:", state.keys() if state else "Empty")
    print("Note from Node A:", state.get("note", "None"))
    
    # Return updated state
    new_state = copy.deepcopy(state)
    new_state["status"] = "completed"
    return new_state

def main():
    """Main function to build and run a minimal test graph"""
    try:
        # Create the workflow
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("node_a", node_a)
        workflow.add_node("node_b", node_b)
        
        # Add edges
        workflow.add_edge("node_a", "node_b")
        workflow.add_edge("node_b", END)
        
        # Set entry point
        workflow.set_entry_point("node_a")
        
        # Compile
        app = workflow.compile()
        
        # Create initial state
        employee = Employee("Test User")
        initial_state = State({"employee": employee})
        
        print("Initial state type:", type(initial_state))
        print("Initial state:", initial_state)
        print("Running workflow...")
        
        # Invoke the workflow
        result = app.invoke(initial_state)
        
        print("Workflow completed!")
        print("Result keys:", result.keys())
        print("Status:", result.get("status", "Unknown"))
        
    except Exception as e:
        print("Error:", type(e).__name__, "-", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 