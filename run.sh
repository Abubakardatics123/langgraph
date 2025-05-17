#!/bin/bash

# Try to run with Python 3 first
echo "Attempting to run with Python 3..."
if command -v python3 &> /dev/null; then
    python3 run_workflow.py
    exit $?
fi

# Fall back to whatever Python is available
echo "Python 3 not found, falling back to system Python..."
python run_workflow.py
exit $? 