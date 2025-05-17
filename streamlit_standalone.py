import streamlit as st
import json
import os
from datetime import datetime
import data_access

# Configure the app
st.set_page_config(
    page_title="HR Workflow Dashboard",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# Functions
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
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username == "admin" and password == "password123":  # Hardcoded for demo
                st.session_state.authenticated = True
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
            st.session_state.employees = data_access.load_employees()
    
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
        # Calculate from created_at timestamp
        now = datetime.now().timestamp()
        week_ago = now - (7 * 24 * 60 * 60)
        recent_count = 0
        
        for emp in employees:
            created_at = emp.get('created_at')
            if created_at:
                try:
                    # Handle ISO format timestamp
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    if created_time > week_ago:
                        recent_count += 1
                except (ValueError, TypeError):
                    pass
        
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
            st.session_state.employees = data_access.load_employees()
    
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
                
                # Add to database
                data_access.add_employee(employee_data)
                
                # Update session state
                st.session_state.employees = data_access.load_employees()
                
                st.success(f"Employee {name} added successfully!")
                st.session_state.active_tab = "Employees"
                st.rerun()

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.title("HR Workflow")
        
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