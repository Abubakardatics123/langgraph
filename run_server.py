#!/usr/bin/env python3
"""
Run the HR Workflow API server with proper configuration
"""

import os
import sys
import subprocess

def run_server():
    """Run the Flask API server"""
    
    print("=== Starting HR Workflow API Server ===")
    
    # Make sure required packages are installed
    try:
        import flask
        import flask_cors
        print("Required packages are installed")
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        print("Packages installed")
    
    # Check if data directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    if not os.path.exists(data_dir):
        print("Creating data directory...")
        os.makedirs(data_dir)
    
    # Set environment variables
    os.environ["FLASK_APP"] = "api.py"
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "1"
    
    # Run the server
    print("Starting server on port 5001...")
    os.environ["PORT"] = "5001"
    
    try:
        from api import app
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server() 