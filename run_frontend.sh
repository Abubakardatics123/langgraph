#!/bin/bash

echo "======================================="
echo "HR ONBOARDING WORKFLOW FRONTEND"
echo "======================================="
echo "Installing dependencies..."
python3 -m pip install flask flask-cors

echo "Setting up frontend..."
if [ ! -d "frontend" ]; then
    mkdir -p frontend/css frontend/js
    echo "Frontend directories created"
fi

echo "Starting the Flask API server..."
python3 api.py 