import os
import json
from typing import Dict, List, TypedDict, Annotated, Sequence, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# Type definitions for our workflow
class EmployeeInfo(TypedDict):
    name: str
    position: str
    department: str
    start_date: str
    employee_id: str
    equipment_needs: List[str]
    system_access: List[str]
    status: str

class WorkflowState(TypedDict):
    employee: EmployeeInfo
    current_step: str
    completed_steps: List[str]
    messages: List[Any]
    documents_ready: List[str]
    feedback: str

# Initialize LLM (using Groq, but this can be changed to any provider)
# You'll need to set GROQ_API_KEY environment variable
api_key = os.environ.get("GROQ_API_KEY", "")
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=api_key)

# Node 1: Documentation Preparation Node
def prepare_documents(state: WorkflowState) -> WorkflowState:
    """Generate a list of required documents based on employee information."""
    # Create a message to ask the LLM for required documents
    employee = state["employee"]
    prompt = f"""
    You are an HR assistant helping with employee onboarding.
    Given the following employee information, list the essential documents needed for onboarding:
    
    Name: {employee['name']}
    Position: {employee['position']}
    Department: {employee['department']}
    Start Date: {employee['start_date']}
    Equipment Needs: {', '.join(employee['equipment_needs'])}
    System Access: {', '.join(employee['system_access'])}
    
    Return ONLY a JSON array of document names without any explanation.
    For example: ["Employment Contract", "Tax Form W-4", "Direct Deposit Form"]
    """
    
    # In a real implementation, you would use the LLM to generate documents
    # For demo purposes, we'll use a hardcoded response for some departments
    if employee["department"] == "Engineering":
        documents = [
            "Employment Contract", 
            "Tax Form W-4", 
            "Direct Deposit Form",
            "NDA Agreement",
            "GitHub Access Form",
            "Equipment Request Form"
        ]
    elif employee["department"] == "Sales":
        documents = [
            "Employment Contract", 
            "Tax Form W-4", 
            "Direct Deposit Form",
            "Sales Compensation Agreement",
            "CRM Access Form",
            "Travel Policy Document"
        ]
    else:
        documents = [
            "Employment Contract", 
            "Tax Form W-4", 
            "Direct Deposit Form",
            "Department Specific Policies"
        ]
    
    # Update state with document list
    state["documents_ready"] = documents
    state["current_step"] = "documents_prepared"
    state["completed_steps"].append("document_preparation")
    state["messages"].append({
        "role": "system",
        "content": f"Documents prepared for {employee['name']}: {', '.join(documents)}"
    })
    
    return state

# Node 2: Personalized Welcome Message
def generate_welcome_message(state: WorkflowState) -> WorkflowState:
    """Generate a personalized welcome message for the new employee."""
    employee = state["employee"]
    documents = state["documents_ready"]
    
    prompt = f"""
    You are an HR assistant responsible for welcoming new employees.
    Craft a warm, professional welcome message for the following new employee:
    
    Name: {employee['name']}
    Position: {employee['position']}
    Department: {employee['department']}
    Start Date: {employee['start_date']}
    
    Include:
    1. A warm welcome
    2. Mention of their specific role and department
    3. What to expect on the first day
    4. Brief mention of required documents: {', '.join(documents)}
    
    Keep it concise and friendly.
    """
    
    # In production, we would call the LLM here
    # messages = [HumanMessage(content=prompt)]
    # welcome_message = llm.invoke(messages).content
    
    # For demo purposes, we'll use a template message
    welcome_message = f"""
    Dear {employee['name']},
    
    Welcome to our team! We're thrilled to have you join us as a {employee['position']} in the {employee['department']} department starting on {employee['start_date']}.
    
    On your first day, please arrive at 9:00 AM at our main office where you'll be greeted by your manager. You'll receive a tour of the facilities, meet your team members, and get set up with all necessary equipment and access.
    
    Please prepare the following documents in advance:
    {', '.join(documents)}
    
    We're looking forward to your contributions and having you on board!
    
    Best regards,
    HR Department
    """
    
    # Update state with welcome message
    state["messages"].append({
        "role": "assistant",
        "content": welcome_message
    })
    state["current_step"] = "welcome_message_sent"
    state["completed_steps"].append("welcome_message")
    
    return state

# Node 3: Equipment Provisioning
def provision_equipment(state: WorkflowState) -> WorkflowState:
    """Generate equipment provisioning requests based on employee needs."""
    employee = state["employee"]
    
    # Get the equipment needs from employee data
    equipment_needs = employee["equipment_needs"]
    
    # Generate provisioning tickets for each equipment
    provisioning_details = []
    for item in equipment_needs:
        # In a real implementation, you might generate actual tickets
        # or integrate with a ticketing system
        ticket_id = f"EQ-{hash(employee['name'] + item) % 10000}"
        provisioning_details.append({
            "item": item,
            "ticket_id": ticket_id,
            "status": "requested",
            "estimated_delivery": "Before start date"
        })
    
    # Create a summary message
    summary = f"""
    Equipment provisioning for {employee['name']}:
    
    {"".join([f"- {item['item']}: Ticket #{item['ticket_id']} ({item['status']})\n" for item in provisioning_details])}
    
    All equipment will be ready by {employee['start_date']}.
    """
    
    # Update state
    state["messages"].append({
        "role": "system",
        "content": summary
    })
    state["current_step"] = "equipment_provisioned"
    state["completed_steps"].append("equipment_provisioning")
    
    return state

# Define our workflow graph
def create_workflow_graph():
    # Initialize the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("document_preparation", prepare_documents)
    workflow.add_node("welcome_message", generate_welcome_message)
    workflow.add_node("equipment_provisioning", provision_equipment)
    
    # Add edges (define the flow)
    workflow.add_edge("document_preparation", "welcome_message")
    workflow.add_edge("welcome_message", "equipment_provisioning")
    workflow.add_edge("equipment_provisioning", END)
    
    # Set the entry point
    workflow.set_entry_point("document_preparation")
    
    # Compile the graph
    return workflow.compile()

# Function to start a new onboarding workflow
def start_onboarding_workflow(employee_data: Dict) -> Dict:
    """Start the onboarding workflow for a new employee."""
    # Prepare the initial state
    initial_state = WorkflowState(
        employee=employee_data,
        current_step="starting",
        completed_steps=[],
        messages=[],
        documents_ready=[],
        feedback=""
    )
    
    # Create the workflow
    workflow = create_workflow_graph()
    
    # Run the workflow
    for event, state in workflow.stream(initial_state):
        print(f"Step completed: {event}")
    
    # Return the final state
    return state

# Example usage
if __name__ == "__main__":
    # Test with a sample employee
    sample_employee = EmployeeInfo(
        name="John Doe",
        position="Software Engineer",
        department="Engineering",
        start_date="2025-06-01",
        employee_id="EMP12345",
        equipment_needs=["Laptop", "Monitor", "Keyboard"],
        system_access=["GitHub", "Jira", "Slack"],
        status="pending"
    )
    
    # Run the workflow
    result = start_onboarding_workflow(sample_employee)
    
    # Print the messages generated during the workflow
    print("\nWorkflow Messages:")
    for message in result["messages"]:
        print(f"\n[{message['role']}]: {message['content']}")
    
    print(f"\nWorkflow completed with steps: {result['completed_steps']}") 