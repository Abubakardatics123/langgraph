#!/bin/bash

echo "======================================="
echo "HR ONBOARDING WORKFLOW"
echo "======================================="
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Python information:"
python --version

# Try to run with Python 3 first
echo "--------------------------------------"
echo "Attempting to run with Python 3..."
if command -v python3 &> /dev/null; then
    python3 run_workflow.py
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "Python 3 run failed with exit code $exit_code"
    else
        exit 0
    fi
fi

# Fall back to whatever Python is available
echo "--------------------------------------"
echo "Falling back to system Python..."
python run_workflow.py
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "--------------------------------------"
    echo "ERROR: Workflow failed with exit code $exit_code"
    echo "Check the messages above for details."
fi
exit $exit_code 