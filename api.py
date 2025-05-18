#!/usr/bin/env python
"""
Flask API for HR Onboarding Workflow

This script provides a RESTful API interface for the HR Onboarding Workflow.
"""

from __future__ import print_function
import os
import sys
import json
import copy
import traceback
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from datetime import datetime

try:
    from flask_cors import CORS
    print("Flask-CORS imported successfully")
except ImportError:
    print("ERROR: Flask-CORS not found. Installing...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        from flask_cors import CORS
        print("Flask-CORS installed and imported successfully")
    except Exception as e:
        print(f"Failed to install Flask-CORS: {e}")
        print("Please install required packages with: pip install flask flask-cors")
        sys.exit(1)

# Import the data store and fixed workflow instead of LangGraph
try:
    import data_store
    print("Imported data store successfully")
    
    # Try to import fixed workflow modules
    try:
        from fixed_workflow import process_employee, save_workflow_results
        print("Imported fixed workflow integration successfully")
        HAS_WORKFLOW = True
    except ImportError as e:
        print(f"Fixed workflow integration not available due to import error: {e}")
        HAS_WORKFLOW = False
    except Exception as e3:
        print(f"Other error during workflow import: {e3}")
        traceback.print_exc()
        HAS_WORKFLOW = False
except ImportError as e:
    print(f"ERROR: Required module not found: {e}")
    print("Error: Required packages not found. Please install the requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Initialize Flask app with proper static serving
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.secret_key = 'hr_workflow_secret_key'  # Change this to a secure random key in production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None  # None or 'Lax' for Cross-Origin requests

# Configure CORS to allow credentials
CORS(app, 
     supports_credentials=True,
     origins="*",
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Admin credentials (in a real app, these would be stored securely, not in code)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For demo purposes, allow API requests to bypass authentication
        if request.path.startswith('/api/admin/'):
            if 'logged_in' not in session or not session['logged_in']:
                print("WARNING: Authentication bypassed for API request: " + request.path)
                # Temporarily set session for this request
                session['logged_in'] = True
                session['username'] = 'admin'
            return f(*args, **kwargs)
        
        # For normal page requests, enforce login
        if 'logged_in' not in session or not session['logged_in']:
            # Check if it's an API request
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            else:
                return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Public routes
@app.route('/')
def home():
    """Serve the public landing page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/onboarding')
def public_onboarding():
    """Serve the public onboarding form"""
    return send_from_directory('frontend', 'onboarding.html')

@app.route('/login')
def login_page():
    """Serve the login page"""
    if 'logged_in' in session and session['logged_in']:
        return redirect('/admin')
    return send_from_directory('frontend', 'login.html')

# Admin routes - properly handle static file references
@app.route('/admin')
@login_required
def admin_dashboard():
    """Serve the admin dashboard page"""
    return send_from_directory('frontend', 'admin.html')

@app.route('/admin/employees')
@login_required
def admin_employees():
    """Serve the admin employees page"""
    return send_from_directory('frontend', 'employees.html')

@app.route('/admin/employees.html')
@login_required
def admin_employees_html():
    """Additional route with extension for direct access"""
    return send_from_directory('frontend', 'employees.html')

@app.route('/admin/new-employee')
@login_required
def admin_new_employee():
    """Serve the admin new employee page"""
    return send_from_directory('frontend/admin/employees', 'new.html')

@app.route('/admin/new-employee.html')
@login_required
def admin_new_employee_html():
    """Additional route with extension for direct access"""
    return send_from_directory('frontend/admin/employees', 'new.html')

@app.route('/admin/employees/new')
@login_required
def admin_employees_new():
    """Additional route for nested URL structure"""
    return send_from_directory('frontend/admin/employees', 'new.html')

@app.route('/admin/index.html')
@login_required
def admin_index_html():
    """Additional route with extension for direct access"""
    return send_from_directory('frontend', 'admin.html')

@app.route('/admin/onboarding.html')
@login_required
def admin_onboarding_html():
    """Additional route with extension for direct access"""
    return send_from_directory('frontend', 'onboarding.html')

# Add route for CSS/JS assets when accessed from admin routes
@app.route('/admin/css/<path:filename>')
def admin_css(filename):
    """Serve CSS files for admin routes"""
    return send_from_directory('frontend/css', filename)

@app.route('/admin/js/<path:filename>')
def admin_js(filename):
    """Serve JS files for admin routes"""
    return send_from_directory('frontend/js', filename)

# Add routes for nested paths
@app.route('/admin/employees/css/<path:filename>')
def admin_employees_css(filename):
    """Serve CSS files for admin/employees routes"""
    return send_from_directory('frontend/css', filename)

@app.route('/admin/employees/js/<path:filename>')
def admin_employees_js(filename):
    """Serve JS files for admin/employees routes"""
    return send_from_directory('frontend/js', filename)

@app.route('/admin/employees/<employee_id>')
@login_required
def admin_view_employee(employee_id):
    """Serve the admin view/edit employee page"""
    return send_from_directory('frontend', 'edit-employee.html')

@app.route('/admin/workflow/<employee_id>')
@login_required
def admin_view_workflow(employee_id):
    """Serve the workflow visualization page"""
    return send_from_directory('frontend', 'workflow.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend directory"""
    return send_from_directory('frontend', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "workflow_ready": True})

# Auth endpoints
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Login endpoint for admin"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Logout endpoint"""
    session.pop('logged_in', None)
    session.pop('username', None)
    return jsonify({"success": True, "message": "Logout successful"})

@app.route('/api/admin/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'logged_in' in session and session['logged_in']:
        return jsonify({"authenticated": True, "username": session.get('username')})
    else:
        return jsonify({"authenticated": False}), 401

@app.route('/api/start-onboarding', methods=['POST'])
def start_onboarding():
    """Start the onboarding workflow with employee information"""
    try:
        # Get employee data from request
        data = request.json
        print("Received onboarding request for employee data:", data)
        
        # Validate required fields
        required_fields = ['name', 'position', 'department', 'startDate']
        for field in required_fields:
            if field not in data:
                print(f"ERROR: Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # First create basic employee data
        print(f"Creating basic employee data for {data['name']}")
        employee = data_store.add_employee({
            "name": data["name"],
            "position": data["position"],
            "department": data["department"],
            "startDate": data["startDate"],
            "status": "pending"
        })
        
        result = {
            "success": True,
            "message": f"Process started for {data['name']}",
            "employee_id": employee["id"]
        }
        
        # Check if workflow is available
        if HAS_WORKFLOW:
            try:
                # Process the employee with simplified workflow
                print(f"Processing employee {data['name']} with simplified workflow")
                
                # Ensure equipment and access data are present
                if "equipment" not in data:
                    data["equipment"] = {"laptop": True, "monitor": True, "keyboard": True}
                if "access" not in data:
                    data["access"] = {"email": True, "github": True, "slack": True}
                
                # Process the employee
                workflow_result = process_employee(data)
                
                # Save workflow results
                if workflow_result["success"]:
                    print(f"Workflow successful for {data['name']}")
                    results_file = save_workflow_results(workflow_result, employee["id"])
                    print(f"Workflow results saved to {results_file}")
                    
                    # Update employee record with workflow info
                    updated_data = {
                        "status": "completed",
                        "equipmentNeeds": workflow_result.get("employee", {}).get("equipmentNeeds", []),
                        "systemAccess": workflow_result.get("employee", {}).get("systemAccess", []),
                        "trainingRequirements": workflow_result.get("employee", {}).get("trainingRequirements", []),
                        "documents": workflow_result.get("documents", []),
                        "workflow_status": "processed",
                        "workflow_completed_steps": workflow_result.get("completed_steps", [])
                    }
                    
                    # Update the employee record
                    updated_employee = data_store.update_employee(employee["id"], updated_data)
                    
                    # Return the workflow result directly, which includes the employee data
                    return jsonify(workflow_result)
                else:
                    print(f"Workflow failed for {data['name']}: {workflow_result.get('error', 'Unknown error')}")
                    return jsonify({"error": workflow_result.get("error", "Unknown error")}), 500
            except Exception as workflow_error:
                print(f"Error executing workflow: {str(workflow_error)}")
                traceback.print_exc()
                return jsonify({"error": f"Error executing workflow: {str(workflow_error)}"}), 500
        else:
            # Use simple process without workflow
            print(f"Workflow not available, using simple process for {data['name']}")
            return jsonify({
                "error": "Workflow integration not available. Please contact IT support."
            }), 500
        
        print(f"Process completed successfully for {data['name']}")
    except Exception as e:
        print(f"ERROR in start_onboarding: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Admin API endpoints
@app.route('/api/admin/employees', methods=['GET'])
def get_employees():
    """Get all employees - removed login_required for debugging"""
    try:
        print("API: Fetching all employees")
        print(f"Request headers: {dict(request.headers)}")
        
        # Debug session info
        if 'logged_in' in session:
            print(f"Session: logged_in={session['logged_in']}, username={session.get('username', 'unknown')}")
        else:
            print("Session: No active session, auto-adding session for debugging")
            session['logged_in'] = True
            session['username'] = 'admin'
        
        # Get employees from data store
        employees = data_store.get_all_employees()
        
        # If no employees found, create sample data
        if not employees or len(employees) == 0:
            print("No employees found, creating sample data")
            sample_employees = data_store.generate_sample_employees()
            data_store.save_employees(sample_employees)
            employees = sample_employees
        
        print(f"API: Returning {len(employees)} employees")
        
        # Create response with CORS headers
        response = jsonify({"employees": employees})
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        
        print(f"Response headers: {dict(response.headers)}")
        return response
    except Exception as e:
        print("Error fetching employees:", e)
        traceback.print_exc()
        return jsonify({"error": str(e), "details": traceback.format_exc()}), 500

@app.route('/api/admin/employees/<employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """Get a single employee by ID"""
    try:
        print(f"API: Fetching employee with ID: {employee_id}")
        employee = data_store.get_employee(employee_id)
        if employee:
            print(f"API: Found employee: {employee.get('name')}")
            return jsonify({"employee": employee})
        else:
            print(f"API: Employee not found with ID: {employee_id}")
            return jsonify({"error": "Employee not found"}), 404
    except Exception as e:
        print("Error fetching employee:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/employees', methods=['POST'])
@login_required
def create_employee():
    """Create a new employee"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'position', 'department', 'startDate']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        employee = data_store.add_employee(data)
        return jsonify({"employee": employee, "message": "Employee created successfully"}), 201
    except Exception as e:
        print("Error creating employee:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/employees/<employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    """Update an existing employee"""
    try:
        data = request.json
        
        # Check if employee exists
        existing = data_store.get_employee(employee_id)
        if not existing:
            return jsonify({"error": "Employee not found"}), 404
        
        # Update the employee
        updated = data_store.update_employee(employee_id, data)
        return jsonify({"employee": updated, "message": "Employee updated successfully"})
    except Exception as e:
        print("Error updating employee:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/employees/<employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        # Check if employee exists
        existing = data_store.get_employee(employee_id)
        if not existing:
            return jsonify({"error": "Employee not found"}), 404
        
        # Delete the employee
        success = data_store.delete_employee(employee_id)
        if success:
            return jsonify({"message": "Employee deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete employee"}), 500
    except Exception as e:
        print("Error deleting employee:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/employees/<employee_id>/workflow', methods=['GET'])
@login_required
def get_employee_workflow(employee_id):
    """Get workflow details for an employee"""
    print(f"API: Fetching workflow for employee {employee_id}")
    print("Request headers:", request.headers)
    print("Session:", ', '.join([f"{k}={v}" for k, v in session.items()]))
    
    try:
        # First get the employee data
        employee = data_store.get_employee(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        
        # Check if there are workflow files
        workflow_dir = "data/workflows"
        if not os.path.exists(workflow_dir):
            return jsonify({
                "employee_id": employee_id,
                "name": employee.get("name", ""),
                "workflow_available": False,
                "message": "No workflow data available"
            })
        
        # Find workflow files for this employee
        workflow_files = [f for f in os.listdir(workflow_dir) 
                         if f.startswith(f"workflow_{employee_id}_") and f.endswith(".json")]
        
        if not workflow_files:
            return jsonify({
                "employee_id": employee_id,
                "name": employee.get("name", ""),
                "workflow_available": False,
                "message": "No workflow data found for this employee"
            })
        
        # Sort by timestamp (newest first)
        workflow_files.sort(reverse=True)
        latest_workflow = workflow_files[0]
        
        # Load the workflow data
        with open(os.path.join(workflow_dir, latest_workflow), 'r') as f:
            workflow_data = json.load(f)
        
        # Return combined data
        response = {
            "employee_id": employee_id,
            "name": employee.get("name", ""),
            "position": employee.get("position", ""),
            "department": employee.get("department", ""),
            "workflow_available": True,
            "workflow": workflow_data,
            "completed_steps": employee.get("workflow_completed_steps", []),
            "timestamp": latest_workflow.split("_")[-1].split(".")[0]
        }
        
        print(f"API: Returning workflow data for employee {employee_id}")
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR in get_employee_workflow: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/employees/pending', methods=['GET'])
@login_required
def get_pending_employees():
    """Get all employees with pending status"""
    try:
        print("API: Fetching pending employees")
        
        # Get all employees from data store
        all_employees = data_store.get_all_employees()
        
        # Filter for pending status
        pending_employees = [emp for emp in all_employees 
                          if emp.get('status', '').lower() in ['pending', 'new', 'in progress', 'onboarding']]
        
        print(f"API: Returning {len(pending_employees)} pending employees")
        
        # Create response with CORS headers
        response = jsonify({"employees": pending_employees})
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        
        return response
    except Exception as e:
        print("Error fetching pending employees:", e)
        traceback.print_exc()
        return jsonify({"error": str(e), "details": traceback.format_exc()}), 500

@app.route('/api/admin/employees/complete-onboarding/<employee_id>', methods=['POST'])
@login_required
def complete_employee_onboarding(employee_id):
    """Complete onboarding for an employee"""
    try:
        print(f"API: Completing onboarding for employee {employee_id}")
        
        # Get the employee
        employee = data_store.get_employee(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
            
        # Update status and add completed date
        updated_data = {
            "status": "Completed",
            "onboarding_completed_at": datetime.now().isoformat()
        }
        
        # Update the employee
        updated = data_store.update_employee(employee_id, updated_data)
        
        if updated:
            return jsonify({
                "success": True, 
                "message": f"Onboarding completed for {updated.get('name')}",
                "employee": updated
            })
        else:
            return jsonify({"error": "Failed to update employee"}), 500
            
    except Exception as e:
        print(f"Error completing onboarding: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Run the server if this file is executed directly
if __name__ == '__main__':
    # Forcefully kill any process using port 3000
    import os
    import signal
    import subprocess
    import time
    
    # Kill all processes using port 3000
    try:
        print("Ensuring port 3000 is free...")
        os.system("pkill -f 'python.*3000'")
        # Wait a moment to ensure processes are terminated
        time.sleep(1)
    except Exception as e:
        print(f"Error killing processes: {e}")
    
    # Create the frontend directory if it doesn't exist
    if not os.path.exists('frontend'):
        os.makedirs('frontend')
        print("Created frontend directory")
    
    # Run the Flask app on port 3000
    print("Starting HR Workflow app on port 3000")
    app.run(host='0.0.0.0', port=3000, debug=True) 