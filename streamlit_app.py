import streamlit as st
import requests
import json
import os
from datetime import datetime
import time

# Try to import the data_access module (for standalone mode)
try:
    import data_access
    HAS_DATA_ACCESS = True
except ImportError:
    HAS_DATA_ACCESS = False

# Configure the app
st.set_page_config(
    page_title="HR Workflow Dashboard",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API endpoints and check connectivity
API_URL = os.environ.get('API_URL', 'http://localhost:5000/api')
EMPLOYEES_API = f"{API_URL}/admin/employees"
AUTH_CHECK_API = f"{API_URL}/admin/check-auth"
LOGIN_API = f"{API_URL}/admin/login"

# Check if API is available
API_AVAILABLE = False
if not os.environ.get('STREAMLIT_STANDALONE', False):
    try:
        # Try to connect to the health endpoint
        health_response = requests.get(f"{API_URL}/health", timeout=3)
        API_AVAILABLE = health_response.status_code == 200
    except:
        st.warning("API server is not available. Using standalone mode with local data.")
        API_AVAILABLE = False

# App state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'api_available' not in st.session_state:
    st.session_state.api_available = API_AVAILABLE

# Functions
def login(username, password):
    # In standalone mode or when API is not available, use hardcoded credentials
    if not st.session_state.api_available:
        if username == "admin" and password == "password123":  # Hardcoded for demo
            st.session_state.authenticated = True
            return True
        else:
            return False
    
    # Otherwise use the API
    try:
        response = requests.post(
            LOGIN_API,
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            st.session_state.authenticated = True
            return True
        else:
            return False
    except Exception as e:
        # If API fails, fall back to hardcoded credentials
        st.warning("Login API not available. Using local authentication.")
        if username == "admin" and password == "password123":  # Hardcoded for demo
            st.session_state.authenticated = True
            return True
        else:
            st.error(f"Login error: {str(e)}")
            return False

def fetch_employees():
    # If API is not available and data_access is available, use local data
    if not st.session_state.api_available and HAS_DATA_ACCESS:
        try:
            employees = data_access.load_employees()
            st.session_state.employees = employees
            return employees
        except Exception as e:
            st.error(f"Error loading local employee data: {str(e)}")
            return []
    
    # Otherwise try to use the API
    try:
        response = requests.get(EMPLOYEES_API)
        if response.status_code == 200:
            data = response.json()
            if 'employees' in data:
                st.session_state.employees = data['employees']
                return data['employees']
        return []
    except Exception as e:
        # If API request fails and data_access is available, try local data as fallback
        if HAS_DATA_ACCESS:
            try:
                st.warning("Falling back to local data.")
                employees = data_access.load_employees()
                st.session_state.employees = employees
                return employees
            except Exception as inner_e:
                st.error(f"Error loading local employee data: {str(inner_e)}")
                return []
        else:
            st.error(f"Error fetching employees: {str(e)}")
            return []

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%b %d, %Y")
    except:
        return date_str

def get_status_color(status):
    if not status:
        return "gray"
    
    status = status.lower()
    if status in ["complete", "completed"]:
        return "green"
    elif status in ["in progress", "inprogress", "in-progress"]:
        return "blue"
    elif status in ["pending", "new"]:
        return "orange"
    else:
        return "gray"

# Login screen
def show_login():
    st.title("HR Workflow Admin Login")
    
    if not st.session_state.api_available:
        st.info("Running in standalone mode with local authentication.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# Dashboard
def show_dashboard():
    st.title("HR Workflow Dashboard")
    
    # Fetch data if needed
    if not st.session_state.employees:
        with st.spinner("Loading data..."):
            fetch_employees()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    employees = st.session_state.employees
    
    with col1:
        st.metric("Total Employees", len(employees))
    
    with col2:
        departments = set([emp.get('department') for emp in employees if emp.get('department')])
        st.metric("Departments", len(departments))
    
    with col3:
        # Recent employees (last 7 days)
        recent_count = 0
        st.metric("Recent Hires", recent_count)
    
    with col4:
        completed_count = len([emp for emp in employees if emp.get('status', '').lower() in ['complete', 'completed']])
        st.metric("Completed Onboarding", completed_count)
    
    # Display employees table
    st.subheader("Employee List")
    
    if not employees:
        st.info("No employees found")
    else:
        # Convert to the format expected by st.dataframe
        employees_data = []
        for emp in employees:
            employees_data.append({
                "Name": emp.get('name', 'N/A'),
                "Position": emp.get('position', 'N/A'),
                "Department": emp.get('department', 'N/A'),
                "Start Date": format_date(emp.get('startDate')),
                "Status": emp.get('status', 'N/A')
            })
        
        st.dataframe(
            employees_data,
            use_container_width=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current onboarding status",
                    width="medium"
                )
            }
        )

# Employee Management
def show_employees():
    st.title("Employee Management")
    
    # Fetch data if needed
    if not st.session_state.employees:
        with st.spinner("Loading data..."):
            fetch_employees()
    
    # Add new employee button
    if st.button("Add New Employee", type="primary"):
        st.session_state.active_tab = "Add Employee"
        st.rerun()
    
    # Display employees in a more detailed way
    st.subheader("Employees")
    
    employees = st.session_state.employees
    
    if not employees:
        st.info("No employees found")
        return
    
    # Create expandable sections for each employee
    for i, emp in enumerate(employees):
        with st.expander(f"{emp.get('name', 'Unknown Employee')} - {emp.get('position', 'No Position')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Department:**", emp.get('department', 'N/A'))
                st.write("**Position:**", emp.get('position', 'N/A'))
                st.write("**Start Date:**", format_date(emp.get('startDate')))
                
                status = emp.get('status', 'N/A')
                st.markdown(f"**Status:** <span style='color:{get_status_color(status)};'>{status}</span>", unsafe_allow_html=True)
            
            with col2:
                if emp.get('equipmentNeeds'):
                    st.write("**Equipment Needs:**")
                    for item in emp.get('equipmentNeeds'):
                        st.write(f"- {item}")
                
                if emp.get('systemAccess'):
                    st.write("**System Access:**")
                    for item in emp.get('systemAccess'):
                        st.write(f"- {item}")

# Add New Employee
def show_add_employee():
    st.title("Add New Employee")
    
    with st.form("add_employee_form"):
        name = st.text_input("Full Name")
        
        col1, col2 = st.columns(2)
        with col1:
            position = st.text_input("Position")
        with col2:
            department = st.selectbox(
                "Department",
                ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "Product"]
            )
        
        start_date = st.date_input("Start Date")
        
        # Default equipment needs based on department
        equipment_col, access_col = st.columns(2)
        
        with equipment_col:
            st.write("**Equipment Needs**")
            laptop = st.checkbox("Laptop", value=True)
            monitor = st.checkbox("Monitor")
            phone = st.checkbox("Phone")
            headset = st.checkbox("Headset")
            
        with access_col:
            st.write("**System Access**")
            email = st.checkbox("Email", value=True)
            crm = st.checkbox("CRM")
            github = st.checkbox("GitHub")
            jira = st.checkbox("Jira")
        
        submitted = st.form_submit_button("Add Employee")
        
        if submitted:
            if not name or not position or not department or not start_date:
                st.error("Please fill out all required fields")
            else:
                # Create employee data
                employee_data = {
                    "name": name,
                    "position": position,
                    "department": department,
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "status": "New",
                    "equipmentNeeds": [],
                    "systemAccess": []
                }
                
                # Add equipment needs
                if laptop: employee_data["equipmentNeeds"].append("Laptop")
                if monitor: employee_data["equipmentNeeds"].append("Monitor")
                if phone: employee_data["equipmentNeeds"].append("Phone")
                if headset: employee_data["equipmentNeeds"].append("Headset")
                
                # Add system access
                if email: employee_data["systemAccess"].append("Email")
                if crm: employee_data["systemAccess"].append("CRM")
                if github: employee_data["systemAccess"].append("GitHub")
                if jira: employee_data["systemAccess"].append("Jira")
                
                success = False
                
                # Try to add via API if available
                if st.session_state.api_available:
                    try:
                        response = requests.post(
                            f"{API_URL}/start-onboarding",
                            json=employee_data,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            success = True
                    except Exception as e:
                        st.error(f"Error adding employee via API: {str(e)}")
                        # Will try fallback below
                
                # If API failed or not available, try using local data access
                if not success and HAS_DATA_ACCESS:
                    try:
                        data_access.add_employee(employee_data)
                        success = True
                    except Exception as e:
                        st.error(f"Error adding employee locally: {str(e)}")
                
                if success:
                    st.success(f"Employee {name} added successfully!")
                    # Update the employees list
                    fetch_employees()
                    st.session_state.active_tab = "Employees"
                    st.rerun()

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.title("HR Workflow")
        
        # Show API status
        if st.session_state.api_available:
            st.success("API Connected")
        else:
            st.warning("Standalone Mode (API Unavailable)")
        
        if st.session_state.authenticated:
            st.write(f"Welcome, Admin!")
            
            # Navigation
            selected = st.radio(
                "Navigation",
                ["Dashboard", "Employees", "Add Employee"],
                index=["Dashboard", "Employees", "Add Employee"].index(st.session_state.active_tab)
            )
            
            if selected != st.session_state.active_tab:
                st.session_state.active_tab = selected
                st.rerun()
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
        else:
            st.info("Please login to continue")
    
    # Main content
    if not st.session_state.authenticated:
        show_login()
    else:
        if st.session_state.active_tab == "Dashboard":
            show_dashboard()
        elif st.session_state.active_tab == "Employees":
            show_employees()
        elif st.session_state.active_tab == "Add Employee":
            show_add_employee()

if __name__ == "__main__":
    main() 