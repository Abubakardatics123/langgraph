#!/bin/bash

# Function to check if port is in use
check_port() {
    lsof -i :"$1" > /dev/null 2>&1
    return $?
}

# Kill all Python processes running api.py
echo "Killing any running Python API processes..."
pkill -f "python.*api.py" || true

# Kill processes using ports 3000 and 5000
echo "Killing all processes using ports 3000 and 5000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Wait to ensure ports are free
echo "Waiting for ports to be freed..."
sleep 2

# Check if port 3000 is still in use
if check_port 3000; then
    echo "Port 3000 is still in use. Please free this port manually and try again."
    exit 1
fi

# Start API server on port 3000
echo "Starting API server on port 3000..."
python3 api.py 