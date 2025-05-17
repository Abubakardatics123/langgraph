#!/usr/bin/env python
"""
HR Onboarding Workflow using LangGraph

This script implements a simple HR onboarding workflow with multiple nodes and memory persistence.
"""

# Import necessary libraries
import os
import sys
import copy  # Add copy module for deepcopy

# Version check
if sys.version_info[0] < 3:
    print("Warning: This script was designed for Python 3 but is running on Python 2")
    print("Some features may not work correctly. Consider running with Python 3 instead.")

try:
    from typing import Dict, List, TypedDict, Annotated, Literal
except ImportError:
    # For Python 2 compatibility, create minimal typing
    Dict = dict
    List = list
    class TypedDict(dict): pass
    Annotated = None
    Literal = None

# Create a simple BaseModel alternative for Python 2
class BaseModel(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __getattr__(self, name):
        # This helps prevent "object has no attribute" errors
        if name not in self.__dict__:
            return None
        return self.__dict__[name]

# LangGraph and LangChain imports
try:
    from langgraph.graph import StateGraph, END
    from langchain_groq import ChatGroq
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    print("Error: Required packages not found. Please install the requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Set Groq API key
os.environ["GROQ_API_KEY"] = "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"

#############################################
# Define State and Memory
#############################################

# Define the state schema - Python 2 compatible version
class EmployeeInfo(object):
    def __init__(self, name, position, department, start_date, 
                 equipment_needs=None, system_access=None, 
                 training_requirements=None, onboarding_status="pending"):
        self.name = name
        self.position = position
        self.department = department
        self.start_date = start_date
        self.equipment_needs = equipment_needs or []
        self.system_access = system_access or []
        self.training_requirements = training_requirements or []
        self.onboarding_status = onboarding_status

# Define the state structure - Python 2 compatible
class State(dict):
    """Custom state class that extends dict to ensure compatibility with LangGraph"""
    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
    
    def copy(self):
        """Return a deep copy of the state"""
        return copy.deepcopy(self)

#############################################
# Define Nodes
#############################################

# Initialize LLM
try:
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
except Exception as e:
    print("Error initializing ChatGroq: {}".format(e))
    print("Check your API key and internet connection.")
    sys.exit(1)

# Node 1: Collect and validate employee information
def collect_employee_info(state):
    """Collect and validate basic employee information"""
    try:
        # Get the employee info from the current state
        if not state:
            print("Error: State is empty")
            print("Current state:", state)
            raise KeyError("State is empty")
            
        if 'employee' not in state:
            print("Error: 'employee' key missing from state")
            print("Current state keys:", state.keys())
            raise KeyError("'employee' key missing from state")
            
        employee = state["employee"]
        print("DEBUG Node 1 - Employee: {}".format(employee.name))
        messages = state.get("messages", [])
        
        # Create a prompt for the LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an HR assistant helping with employee onboarding. "
                      "Validate the following employee information and add any missing details."),
            ("user", "Employee Name: {name}\n"
                    "Position: {position}\n"
                    "Department: {department}\n"
                    "Start Date: {start_date}")
        ])
        
        # Format the prompt with employee info
        formatted_prompt = prompt.format(
            name=employee.name,
            position=employee.position,
            department=employee.department,
            start_date=employee.start_date
        )
        
        # Get response from LLM - fixing the content attribute issue
        human_message = HumanMessage(content=str(formatted_prompt))
        response = llm.invoke([human_message])
        
        # Store the message in memory
        messages.append({"role": "user", "content": str(formatted_prompt)})
        messages.append({"role": "assistant", "content": response.content})
        
        # Add a note to HR notes
        hr_notes = state.get("hr_notes", [])
        hr_notes.append("Employee information validated for {}".format(employee.name))
        
        # Return updated state
        new_state = copy.deepcopy(state)
        new_state["hr_notes"] = hr_notes
        new_state["messages"] = messages
        return new_state
    except Exception as e:
        print("Error in collect_employee_info node: {}".format(e))
        import traceback
        traceback.print_exc()
        raise

# Node 2: Determine equipment and access needs
def determine_equipment_access(state):
    """Determine equipment and system access needs based on role"""
    try:
        # Get the employee info and messages from the current state
        if 'employee' not in state:
            print("Error: 'employee' key missing from state")
            print("Current state keys:", state.keys())
            raise KeyError("'employee' key missing from state")
            
        employee = state["employee"]
        print("DEBUG Node 2 - Employee: {}".format(employee.name))
        messages = state.get("messages", [])
        
        # Create a prompt for the LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an IT specialist helping with employee onboarding. "
                      "Determine appropriate equipment and system access based on the role."),
            ("user", "Based on the following employee information, list required equipment and system access:\n"
                    "Employee Name: {name}\n"
                    "Position: {position}\n"
                    "Department: {department}\n"
                    "Respond in JSON format with 'equipment_needs' and 'system_access' as lists.")
        ])
        
        # Format the prompt with employee info
        formatted_prompt = prompt.format(
            name=employee.name,
            position=employee.position,
            department=employee.department
        )
        
        # Define output parser for structured response
        parser = JsonOutputParser()
        
        # Get response from LLM and parse
        chain = prompt | llm | parser
        response = chain.invoke({
            "name": employee.name, 
            "position": employee.position, 
            "department": employee.department
        })
        
        # Update employee information
        employee.equipment_needs = response.get("equipment_needs", [])
        employee.system_access = response.get("system_access", [])
        
        # Store the interaction in memory
        messages.append({"role": "user", "content": formatted_prompt.content})
        messages.append({"role": "assistant", "content": str(response)})
        
        # Add notes
        it_notes = state.get("it_notes", [])
        it_notes.append("Equipment and access determined for {}".format(employee.name))
        
        # Return updated state with memory
        new_state = copy.deepcopy(state)
        new_state["employee"] = employee
        new_state["it_notes"] = it_notes
        new_state["messages"] = messages
        return new_state
    except Exception as e:
        print("Error in determine_equipment_access node: {}".format(e))
        import traceback
        traceback.print_exc()
        raise

# Node 3: Create training plan
def create_training_plan(state):
    """Create personalized training plan for the new employee"""
    try:
        # Get the employee info and message history
        if 'employee' not in state:
            print("Error: 'employee' key missing from state")
            print("Current state keys:", state.keys())
            raise KeyError("'employee' key missing from state")
            
        employee = state["employee"]
        print("DEBUG Node 3 - Employee: {}".format(employee.name))
        messages = state.get("messages", [])
        
        # Use message history for context
        conversation_history = "\n".join(["{}:{}".format(msg['role'], msg['content']) for msg in messages[-4:]])
        
        # Create a prompt for the LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a training coordinator helping with employee onboarding. "
                      "Create a training plan for the new employee."),
            ("user", "Based on the following employee information and previous onboarding steps, "
                    "determine appropriate training requirements:\n"
                    "Employee Name: {name}\n"
                    "Position: {position}\n"
                    "Department: {department}\n"
                    "Equipment: {equipment}\n"
                    "System Access: {access}\n\n"
                    "Context from previous steps:\n{context}\n\n"
                    "Respond in JSON format with 'training_requirements' as a list.")
        ])
        
        # Format the prompt with employee info and context
        formatted_prompt = prompt.format(
            name=employee.name,
            position=employee.position,
            department=employee.department,
            equipment=employee.equipment_needs,
            access=employee.system_access,
            context=conversation_history
        )
        
        # Define output parser
        parser = JsonOutputParser()
        
        # Get response from LLM and parse
        chain = prompt | llm | parser
        response = chain.invoke({
            "name": employee.name, 
            "position": employee.position, 
            "department": employee.department,
            "equipment": employee.equipment_needs,
            "access": employee.system_access,
            "context": conversation_history
        })
        
        # Update employee information
        employee.training_requirements = response.get("training_requirements", [])
        employee.onboarding_status = "completed"
        
        # Store the interaction in memory
        messages.append({"role": "user", "content": formatted_prompt.content})
        messages.append({"role": "assistant", "content": str(response)})
        
        # Add notes
        hr_notes = state.get("hr_notes", [])
        hr_notes.append("Training plan created for {}".format(employee.name))
        
        # Return updated state
        new_state = copy.deepcopy(state)
        new_state["employee"] = employee
        new_state["hr_notes"] = hr_notes
        new_state["messages"] = messages
        return new_state
    except Exception as e:
        print("Error in create_training_plan node: {}".format(e))
        import traceback
        traceback.print_exc()
        raise

#############################################
# Building the Workflow Graph
#############################################

def build_workflow():
    try:
        # Create the workflow graph
        workflow = StateGraph(State)
        
        # Add nodes to the graph
        workflow.add_node("collect_employee_info", collect_employee_info)
        workflow.add_node("determine_equipment_access", determine_equipment_access)
        workflow.add_node("create_training_plan", create_training_plan)
        
        # Define edges in the graph
        workflow.add_edge("collect_employee_info", "determine_equipment_access")
        workflow.add_edge("determine_equipment_access", "create_training_plan")
        workflow.add_edge("create_training_plan", END)
        
        # Set the entry point
        workflow.set_entry_point("collect_employee_info")
        
        # Compile the graph with no special options for better compatibility
        return workflow.compile()
    except Exception as e:
        print("Error building workflow: {}".format(e))
        import traceback
        traceback.print_exc()
        raise

#############################################
# Running the Workflow
#############################################

def run_workflow():
    try:
        # Build the workflow
        app = build_workflow()
        
        # Initialize the employee information
        initial_employee = EmployeeInfo(
            name="John Doe",
            position="Software Engineer",
            department="Engineering",
            start_date="2023-12-01"
        )
        
        print("DEBUG: Created employee with name: {}".format(initial_employee.name))
        
        # Initialize the state
        initial_state = {
            "employee": initial_employee,
            "hr_notes": [],
            "it_notes": [],
            "messages": []
        }
        
        print("DEBUG: Initial state keys: {}".format(initial_state.keys()))
        print("DEBUG: Employee in initial state: {}".format("Yes" if "employee" in initial_state else "No"))
        
        # Run the workflow
        print("Starting HR onboarding workflow...\n")
        result = app.invoke(initial_state)
        
        # Print the results
        print("ONBOARDING WORKFLOW RESULTS\n")
        print("Employee: {}".format(result['employee'].name))
        print("Position: {}".format(result['employee'].position))
        print("Department: {}".format(result['employee'].department))
        print("Start Date: {}".format(result['employee'].start_date))
        print("\nEquipment Needs:")
        for item in result['employee'].equipment_needs:
            print("- {}".format(item))
        print("\nSystem Access:")
        for item in result['employee'].system_access:
            print("- {}".format(item))
        print("\nTraining Requirements:")
        for item in result['employee'].training_requirements:
            print("- {}".format(item))
        print("\nStatus: {}".format(result['employee'].onboarding_status))
        
        print("\nHR Notes:")
        for note in result['hr_notes']:
            print("- {}".format(note))
        print("\nIT Notes:")
        for note in result['it_notes']:
            print("- {}".format(note))
        
        # Display memory information
        print("\nMEMORY USAGE:")
        print("Total messages stored: {}".format(len(result['messages'])))
        print("Memory provides context across nodes, allowing the workflow to reference previous steps.")
        
        return result
    except KeyError as e:
        print("Key Error in workflow: {}".format(e))
        import traceback
        traceback.print_exc()
        raise
    except Exception as e:
        print("Error running workflow: {}".format(e))
        import traceback
        traceback.print_exc()
        raise

#############################################
# Main function
#############################################

if __name__ == "__main__":
    try:
        result = run_workflow()
    except Exception as e:
        print("Error running workflow: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1) 