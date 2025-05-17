#!/usr/bin/env python
"""
Run the HR Onboarding Workflow

This script executes the LangGraph-based HR onboarding workflow
Compatible with both Python 2.7 and Python 3.x
"""

from __future__ import print_function  # For Python 2 compatibility

import sys

# Version check
if sys.version_info[0] < 3:
    print("Warning: Running with Python 2.x - some features may be limited")

# Import the workflow function
try:
    from hr_onboarding_workflow import run_workflow
except ImportError as e:
    print("Error importing workflow module: {}".format(e))
    print("Make sure all requirements are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    print("="*50)
    print("HR ONBOARDING WORKFLOW DEMO")
    print("="*50)
    print("\nThis demo shows a LangGraph workflow for employee onboarding with memory persistence.\n")
    
    try:
        result = run_workflow()
        print("\n"+"="*50)
        print("Workflow completed successfully!")
        print("="*50)
    except Exception as e:
        print("\nError running workflow: {}".format(e))
        print("Make sure you've set your Groq API key in the hr_onboarding_workflow.py file.") 