#!/usr/bin/env python3
"""
Run the HR Onboarding Workflow

This script executes the LangGraph-based HR onboarding workflow
"""

from hr_onboarding_workflow import run_workflow

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
        print(f"\nError running workflow: {e}")
        print("Make sure you've set your OpenAI API key in the hr_onboarding_workflow.py file.") 