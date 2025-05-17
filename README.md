# HR Onboarding Workflow with LangGraph

This project demonstrates a simple LangGraph-based workflow for HR employee onboarding processes.

## Features

- Multi-node workflow architecture
- Memory persistence across workflow steps
- AI-powered recommendations for equipment, system access, and training
- Complete onboarding pipeline from initial information to training plan

## Requirements

- Python 3.8+
- Required packages:
  - langgraph
  - langchain
  - langchain_openai
  - langchain_community
  - pydantic

## Getting Started

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Add your OpenAI API key in the `hr_onboarding_workflow.py` file
   ```python
   os.environ["OPENAI_API_KEY"] = "your-api-key-here"
   ```

3. Run the workflow:
   ```
   python run_workflow.py
   ```

## Workflow Architecture

The workflow consists of three main nodes:

1. **Employee Information Collection**: Validates and processes basic employee details
2. **Equipment & Access Determination**: Determines hardware and system access requirements based on role
3. **Training Plan Creation**: Generates a personalized training plan using context from previous steps

Memory is maintained throughout the workflow, allowing each node to access information and context from previous steps.

## Files

- `hr_onboarding_workflow.py` - Core implementation of the LangGraph workflow
- `run_workflow.py` - Simple script to execute the workflow
- `requirements.txt` - Required Python packages

## Extending the Workflow

This simple workflow can be extended with:
- Additional decision nodes
- Integration with HR systems
- Automated email notifications
- Document generation capabilities 