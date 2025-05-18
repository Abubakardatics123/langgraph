import os
import json
from typing import Dict, List, TypedDict, Annotated, Sequence, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph_checkpoint import MemorySaver

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
    memory: Dict[str, Any]  # New field for persistent memory

# Initialize LLM (using Groq, but this can be changed to any provider)
# You'll need to set GROQ_API_KEY environment variable
api_key = os.environ.get("GROQ_API_KEY", "")
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=api_key)

# Create storage for workflow persistence
memory_saver = MemorySaver()

# Node 1: Documentation Preparation Node
def prepare_documents(state: WorkflowState) -> WorkflowState:
    """Generate a list of required documents based on employee information."""
    # Initialize memory if not present
    if "memory" not in state:
        state["memory"] = {}
    
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
    
    # Add to memory
    state["memory"]["documents_generated_at"] = datetime.now().isoformat()
    state["memory"]["document_requirements"] = {
        "based_on_department": employee["department"],
        "based_on_position": employee["position"]
    }
    
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
    
    # Access memory from previous step
    document_requirements = state["memory"].get("document_requirements", {})
    documents_generated_at = state["memory"].get("documents_generated_at", "unknown time")
    
    # Add context about document generation to the prompt
    prompt = f"""
    You are an HR assistant responsible for welcoming new employees.
    Craft a warm, professional welcome message for the following new employee:
    
    Name: {employee['name']}
    Position: {employee['position']}
    Department: {employee['department']}
    Start Date: {employee['start_date']}
    
    The document requirements were prepared at {documents_generated_at} 
    based on the employee's department ({document_requirements.get('based_on_department', 'unknown')})
    and position ({document_requirements.get('based_on_position', 'unknown')}).
    
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
    
    # For demo purposes, we'll use a template message with memory context
    welcome_message = f"""
    Dear {employee['name']},
    
    Welcome to our team! We're thrilled to have you join us as a {employee['position']} in the {employee['department']} department starting on {employee['start_date']}.
    
    On your first day, please arrive at 9:00 AM at our main office where you'll be greeted by your manager. You'll receive a tour of the facilities, meet your team members, and get set up with all necessary equipment and access.
    
    Based on your role in {employee['department']}, we've prepared the following documents for you:
    {', '.join(documents)}
    
    We're looking forward to your contributions and having you on board!
    
    Best regards,
    HR Department
    """
    
    # Add to memory
    state["memory"]["welcome_message_generated_at"] = datetime.now().isoformat()
    state["memory"]["sentiment"] = "positive"
    
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
    
    # Access memory from previous steps
    welcome_message_time = state["memory"].get("welcome_message_generated_at", "unknown time")
    document_requirements = state["memory"].get("document_requirements", {})
    
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
            "estimated_delivery": "Before start date",
            "priority": "High" if item in ["Laptop", "Phone"] else "Normal"
        })
    
    # Create a summary message with context from memory
    summary = f"""
    Equipment provisioning for {employee['name']}:
    
    {"".join([f"- {item['item']}: Ticket #{item['ticket_id']} ({item['status']}, Priority: {item['priority']})\n" for item in provisioning_details])}
    
    All equipment will be ready by {employee['start_date']}.
    
    Note: Welcome message was sent at {welcome_message_time}
    Equipment requirements are based on the employee's role as {employee['position']} in {employee['department']}.
    """
    
    # Add to memory
    state["memory"]["equipment_provisioned_at"] = datetime.now().isoformat()
    state["memory"]["equipment_details"] = [
        {"item": item["item"], "ticket_id": item["ticket_id"]} 
        for item in provisioning_details
    ]
    
    # Update state
    state["messages"].append({
        "role": "system",
        "content": summary
    })
    state["current_step"] = "equipment_provisioned"
    state["completed_steps"].append("equipment_provisioning")
    
    return state

# Define our workflow graph with persistence
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
    
    # Configure persistence
    persisted_workflow = workflow.compile(checkpointer=memory_saver)
    
    return persisted_workflow

# Function to start a new onboarding workflow
def start_onboarding_workflow(employee_data: Dict) -> Dict:
    """Start the onboarding workflow for a new employee."""
    # Prepare the initial state with memory
    initial_state = WorkflowState(
        employee=employee_data,
        current_step="starting",
        completed_steps=[],
        messages=[],
        documents_ready=[],
        feedback="",
        memory={}  # Initialize empty memory
    )
    
    # Create the workflow
    workflow = create_workflow_graph()
    
    # Generate a unique thread ID for this workflow
    thread_id = f"thread_{employee_data['employee_id']}_{datetime.now().timestamp()}"
    
    # Run the workflow with persistence
    for event, state in workflow.stream(initial_state, thread_id=thread_id):
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
    
    # Print memory state
    print("\nMemory State:")
    for key, value in result["memory"].items():
        print(f"{key}: {value}")
    
    print(f"\nWorkflow completed with steps: {result['completed_steps']}") 