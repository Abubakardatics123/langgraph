# HR Onboarding Workflow with LangGraph

This project demonstrates a simple LangGraph-based workflow for HR employee onboarding processes.

## Features

- Multi-node workflow architecture
- Memory persistence across workflow steps
- AI-powered recommendations for equipment, system access, and training
- Complete onboarding pipeline from initial information to training plan
- Web-based user interface for easy interaction

## Requirements

- Python 3.8+ (this code does NOT work with Python 2.x)
- Required packages:
  - langgraph
  - langchain
  - langchain_groq
  - langchain_community
  - pydantic
  - flask
  - flask-cors

## Getting Started

1. Make sure you have Python 3 installed and properly configured:
   ```
   python3 --version
   ```

2. Install the required packages:
   ```
   pip3 install -r requirements.txt
   ```

3. Run the workflow using one of these methods:
   ```
   # Method 1: Using the shell script (recommended)
   ./run.sh
   
   # Method 2: Using Python 3 explicitly
   python3 run_workflow.py
   
   # Method 3: Execute the main script directly (requires proper execution permissions)
   ./hr_onboarding_workflow.py
   ```

## Using the Web Interface

1. Start the web frontend:
   ```
   ./run_frontend.sh
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Fill out the employee information form and submit to run the workflow
4. View the results, including equipment needs, system access requirements, and training plan

## Workflow Architecture

The workflow consists of three main nodes:

1. **Employee Information Collection**: Validates and processes basic employee details
2. **Equipment & Access Determination**: Determines hardware and system access requirements based on role
3. **Training Plan Creation**: Generates a personalized training plan using context from previous steps

Memory is maintained throughout the workflow, allowing each node to access information and context from previous steps.

## Files

- `hr_onboarding_workflow.py` - Core implementation of the LangGraph workflow
- `run_workflow.py` - Simple script to execute the workflow
- `run.sh` - Shell script to ensure the workflow runs with Python 3
- `requirements.txt` - Required Python packages
- `api.py` - Flask API to serve the frontend and handle workflow requests
- `frontend/` - Web interface for interacting with the workflow

## Extending the Workflow

This simple workflow can be extended with:
- Additional decision nodes
- Integration with HR systems
- Automated email notifications
- Document generation capabilities

## Troubleshooting

- If you encounter a SyntaxError, make sure you're using Python 3, not Python 2.7
- The code uses type annotations which are not supported in Python 2.x 
- If the web interface doesn't load, ensure Flask is installed and the API server is running
- Check the console for any error messages if the workflow doesn't complete properly 