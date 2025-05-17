#!/usr/bin/env python3
"""
Simplified HR Onboarding Workflow

This script implements the HR workflow without the full complexity of LangGraph.
It's a temporary solution to ensure we can get the frontend working.
"""

import os
import sys
import copy
from hr_onboarding_workflow import EmployeeInfo, llm, ChatPromptTemplate, JsonOutputParser, HumanMessage

# Set Groq API key (using the one from original workflow)
os.environ["GROQ_API_KEY"] = "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"

def process_onboarding(employee_data):
    """Process the onboarding workflow with the provided employee data"""
    try:
        # Create employee object
        employee = EmployeeInfo(
            name=employee_data["name"],
            position=employee_data["position"],
            department=employee_data["department"],
            start_date=employee_data["startDate"]
        )
        
        # Initialize state
        state = {
            "employee": employee,
            "hr_notes": [],
            "it_notes": [],
            "messages": []
        }
        
        # Run step 1: Collect employee info
        print("Step 1: Collecting employee info")
        state = collect_employee_info(state)
        
        # Run step 2: Determine equipment and access
        print("Step 2: Determining equipment and access")
        state = determine_equipment_access(state)
        
        # Run step 3: Create training plan
        print("Step 3: Creating training plan")
        state = create_training_plan(state)
        
        # Prepare result
        result = {
            "employee": {
                "name": state["employee"].name,
                "position": state["employee"].position,
                "department": state["employee"].department,
                "startDate": state["employee"].start_date,
                "equipmentNeeds": state["employee"].equipment_needs,
                "systemAccess": state["employee"].system_access,
                "trainingRequirements": state["employee"].training_requirements,
                "status": state["employee"].onboarding_status
            },
            "hrNotes": state["hr_notes"],
            "itNotes": state["it_notes"],
            "messageCount": len(state["messages"])
        }
        
        return result
        
    except Exception as e:
        print("Error in process_onboarding:", e)
        import traceback
        traceback.print_exc()
        raise

def collect_employee_info(state):
    """Collect and validate basic employee information"""
    try:
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
        print("Error in collect_employee_info:", e)
        import traceback
        traceback.print_exc()
        raise

def determine_equipment_access(state):
    """Determine equipment and system access needs based on role"""
    try:
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
        formatted_prompt = prompt.format(
            name=employee.name,
            position=employee.position,
            department=employee.department
        )
        messages.append({"role": "user", "content": str(formatted_prompt)})
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
        print("Error in determine_equipment_access:", e)
        import traceback
        traceback.print_exc()
        raise

def create_training_plan(state):
    """Create personalized training plan for the new employee"""
    try:
        employee = state["employee"]
        messages = state.get("messages", [])
        
        # Use message history for context
        conversation_history = "\n".join(["{}:{}".format(msg['role'], msg['content']) for msg in messages[-4:]])
        
        # Create a prompt for the LLM with clearer JSON formatting instructions
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a training coordinator helping with employee onboarding. "
                      "Create a training plan for the new employee. "
                      "Your response MUST be valid JSON with double quotes, containing ONLY a 'training_requirements' list "
                      "with no additional text before or after the JSON."),
            ("user", "Based on the following employee information and previous onboarding steps, "
                    "determine appropriate training requirements:\n"
                    "Employee Name: {name}\n"
                    "Position: {position}\n"
                    "Department: {department}\n"
                    "Equipment: {equipment}\n"
                    "System Access: {access}\n\n"
                    "Context from previous steps:\n{context}\n\n"
                    "Return a JSON object with only a 'training_requirements' key containing an array of strings. "
                    "Do not include any explanations or text outside the JSON.")
        ])
        
        # Define output parser with robust error handling
        parser = JsonOutputParser()
        
        try:
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
            
        except Exception as json_error:
            # Fallback if JSON parsing fails
            print(f"JSON parsing failed: {json_error}")
            print("Using fallback approach to extract training requirements")
            
            # Get raw response from LLM
            raw_prompt = prompt.format(
                name=employee.name,
                position=employee.position,
                department=employee.department,
                equipment=employee.equipment_needs,
                access=employee.system_access,
                context=conversation_history
            )
            
            message = HumanMessage(content=str(raw_prompt))
            llm_response = llm.invoke([message])
            content = llm_response.content
            
            # Try to extract JSON manually
            import re
            import json
            
            # Try to find JSON block
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                # Replace single quotes with double quotes
                json_str = json_str.replace("'", '"')
                
                try:
                    response = json.loads(json_str)
                except json.JSONDecodeError:
                    # Last resort fallback
                    response = {
                        "training_requirements": [
                            "Company Orientation",
                            "Department Training",
                            "Role-specific Training",
                            "System Access Training",
                            "Equipment Training"
                        ]
                    }
            else:
                # Last resort fallback
                response = {
                    "training_requirements": [
                        "Company Orientation",
                        "Department Training",
                        "Role-specific Training",
                        "System Access Training",
                        "Equipment Training"
                    ]
                }
        
        # Update employee information
        employee.training_requirements = response.get("training_requirements", [])
        employee.onboarding_status = "completed"
        
        # Store the interaction in memory
        formatted_prompt = prompt.format(
            name=employee.name,
            position=employee.position,
            department=employee.department,
            equipment=employee.equipment_needs,
            access=employee.system_access,
            context=conversation_history
        )
        messages.append({"role": "user", "content": str(formatted_prompt)})
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
        print("Error in create_training_plan:", e)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Test the simplified workflow
    test_data = {
        "name": "Jane Smith",
        "position": "Marketing Manager",
        "department": "Marketing",
        "startDate": "2023-06-15"
    }
    
    try:
        result = process_onboarding(test_data)
        print("\nWorkflow completed successfully!")
        print("Equipment needs:", result["employee"]["equipmentNeeds"])
        print("System access:", result["employee"]["systemAccess"])
        print("Training requirements:", result["employee"]["trainingRequirements"])
    except Exception as e:
        print("Test failed:", e) 