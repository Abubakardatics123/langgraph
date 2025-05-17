"""
HR Onboarding Workflow using LangGraph

This script implements a simple HR onboarding workflow with multiple nodes and memory persistence.
"""

# Import necessary libraries
import os
from typing import Dict, List, TypedDict, Annotated, Literal
from pydantic import BaseModel

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# Set Groq API key
os.environ["GROQ_API_KEY"] = "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"

#############################################
# Define State and Memory
#############################################

# Define the state schema
class EmployeeInfo(BaseModel):
    name: str
    position: str
    department: str
    start_date: str
    equipment_needs: List[str] = []
    system_access: List[str] = []
    training_requirements: List[str] = []
    onboarding_status: str = "pending"

# Define the state structure
class State(TypedDict):
    employee: EmployeeInfo
    hr_notes: List[str]
    it_notes: List[str]
    messages: List[Dict]  # Memory for conversation messages

#############################################
# Define Nodes
#############################################

# Initialize LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0)

# Node 1: Collect and validate employee information
def collect_employee_info(state: State) -> State:
    """Collect and validate basic employee information"""
    # Get the employee info from the current state
    employee = state["employee"]
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
    
    # Get response from LLM
    response = llm.invoke([HumanMessage(content=formatted_prompt.content)])
    
    # Store the message in memory
    messages.append({"role": "user", "content": formatted_prompt.content})
    messages.append({"role": "assistant", "content": response.content})
    
    # Add a note to HR notes
    hr_notes = state.get("hr_notes", [])
    hr_notes.append(f"Employee information validated for {employee.name}")
    
    # Return updated state
    return {
        **state,
        "hr_notes": hr_notes,
        "messages": messages
    }

# Node 2: Determine equipment and access needs
def determine_equipment_access(state: State) -> State:
    """Determine equipment and system access needs based on role"""
    # Get the employee info and messages from the current state
    employee = state["employee"]
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
    response = chain.invoke({"name": employee.name, "position": employee.position, "department": employee.department})
    
    # Update employee information
    employee.equipment_needs = response.get("equipment_needs", [])
    employee.system_access = response.get("system_access", [])
    
    # Store the interaction in memory
    messages.append({"role": "user", "content": formatted_prompt.content})
    messages.append({"role": "assistant", "content": str(response)})
    
    # Add notes
    it_notes = state.get("it_notes", [])
    it_notes.append(f"Equipment and access determined for {employee.name}")
    
    # Return updated state with memory
    return {
        **state,
        "employee": employee,
        "it_notes": it_notes,
        "messages": messages
    }

# Node 3: Create training plan
def create_training_plan(state: State) -> State:
    """Create personalized training plan for the new employee"""
    # Get the employee info and message history
    employee = state["employee"]
    messages = state.get("messages", [])
    
    # Use message history for context
    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-4:]])
    
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
    hr_notes.append(f"Training plan created for {employee.name}")
    
    # Return updated state
    return {
        **state,
        "employee": employee,
        "hr_notes": hr_notes,
        "messages": messages
    }

#############################################
# Building the Workflow Graph
#############################################

def build_workflow():
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
    
    # Compile the graph
    return workflow.compile()

#############################################
# Running the Workflow
#############################################

def run_workflow():
    # Build the workflow
    app = build_workflow()
    
    # Initialize the employee information
    initial_employee = EmployeeInfo(
        name="John Doe",
        position="Software Engineer",
        department="Engineering",
        start_date="2023-12-01"
    )
    
    # Initialize the state
    initial_state = {
        "employee": initial_employee,
        "hr_notes": [],
        "it_notes": [],
        "messages": []
    }
    
    # Run the workflow
    print("Starting HR onboarding workflow...\n")
    result = app.invoke(initial_state)
    
    # Print the results
    print("ONBOARDING WORKFLOW RESULTS\n")
    print(f"Employee: {result['employee'].name}")
    print(f"Position: {result['employee'].position}")
    print(f"Department: {result['employee'].department}")
    print(f"Start Date: {result['employee'].start_date}")
    print("\nEquipment Needs:")
    for item in result['employee'].equipment_needs:
        print(f"- {item}")
    print("\nSystem Access:")
    for item in result['employee'].system_access:
        print(f"- {item}")
    print("\nTraining Requirements:")
    for item in result['employee'].training_requirements:
        print(f"- {item}")
    print("\nStatus:", result['employee'].onboarding_status)
    
    print("\nHR Notes:")
    for note in result['hr_notes']:
        print(f"- {note}")
    print("\nIT Notes:")
    for note in result['it_notes']:
        print(f"- {note}")
    
    # Display memory information
    print("\nMEMORY USAGE:")
    print(f"Total messages stored: {len(result['messages'])}")
    print("Memory provides context across nodes, allowing the workflow to reference previous steps.")
    
    return result

#############################################
# Main function
#############################################

if __name__ == "__main__":
    result = run_workflow() 