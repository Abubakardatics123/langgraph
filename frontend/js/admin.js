/**
 * HR Workflow Admin Panel JavaScript
 * Handles all the admin functionality including:
 * - Dashboard statistics
 * - Employee listing
 * - CRUD operations for employees
 * - Authentication
 */

// DOM References
const dashboardSection = document.getElementById('dashboard-section');
const employeesSection = document.getElementById('employees-section');
const navDashboard = document.getElementById('nav-dashboard');
const navEmployees = document.getElementById('nav-employees');
const pageTitle = document.getElementById('page-title');
const refreshBtn = document.getElementById('refresh-btn');
const addEmployeeBtn = document.getElementById('add-employee-btn');

// Employee form elements
const employeeForm = document.getElementById('employee-form');
const employeeModal = new bootstrap.Modal(document.getElementById('employeeModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
const employeeIdField = document.getElementById('employee-id');
const detailsSection = document.getElementById('details-section');
const saveBtn = document.getElementById('save-btn');
const deleteBtn = document.getElementById('delete-btn');
const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

// Statistics elements
const totalEmployeesEl = document.getElementById('total-employees');
const totalDepartmentsEl = document.getElementById('total-departments');
const recentEmployeesEl = document.getElementById('recent-employees');
const completedOnboardingEl = document.getElementById('completed-onboarding');

// API endpoints
const API_URL = '/api';
const EMPLOYEES_API = `${API_URL}/admin/employees`;
const AUTH_CHECK_API = `${API_URL}/admin/check-auth`;
const LOGOUT_API = `${API_URL}/admin/logout`;

// Global state
let employees = [];
let currentEmployeeId = null;
let currentUser = null;

// Initialize the admin panel
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication first
    checkAuthentication().then(isAuthenticated => {
        if (isAuthenticated) {
            // Fetch initial data
            fetchEmployees();

            // Setup event listeners
            setupEventListeners();
            
            // Add logout button to nav if not already there
            addLogoutButton();
        } else {
            // Redirect to login if not authenticated
            window.location.href = '/login';
        }
    });
});

/**
 * Check if the user is authenticated
 */
async function checkAuthentication() {
    try {
        const response = await fetch(AUTH_CHECK_API);
        if (response.ok) {
            const data = await response.json();
            currentUser = data.username;
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
        return false;
    }
}

/**
 * Add a logout button to the navigation
 */
function addLogoutButton() {
    // Check if the logout button already exists
    if (document.getElementById('logout-btn')) {
        return;
    }
    
    // Get the sidebar navigation
    const sidebar = document.querySelector('.sidebar .nav');
    
    // Create logout button
    const logoutItem = document.createElement('li');
    logoutItem.className = 'nav-item mt-auto';
    logoutItem.innerHTML = `
        <a class="nav-link" href="#" id="logout-btn">
            <i class="fas fa-sign-out-alt me-2"></i>
            Logout
        </a>
    `;
    
    // Add user info
    const userItem = document.createElement('li');
    userItem.className = 'nav-item mt-auto';
    userItem.innerHTML = `
        <div class="text-center text-white py-4">
            <i class="fas fa-user-circle fa-2x mb-2"></i>
            <p class="mb-0">Logged in as</p>
            <p class="fw-bold">${currentUser || 'Admin'}</p>
        </div>
    `;
    
    // Add to sidebar
    sidebar.appendChild(document.createElement('hr'));
    sidebar.appendChild(userItem);
    sidebar.appendChild(logoutItem);
    
    // Add event listener for logout
    document.getElementById('logout-btn').addEventListener('click', logoutUser);
}

/**
 * Logout user
 */
async function logoutUser() {
    try {
        const response = await fetch(LOGOUT_API, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Redirect to login page
            window.location.href = '/login';
        } else {
            console.error('Logout failed');
            alert('Failed to logout. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('An error occurred during logout. Please try again.');
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Navigation
    navDashboard.addEventListener('click', showDashboard);
    navEmployees.addEventListener('click', showEmployees);
    
    // Buttons
    refreshBtn.addEventListener('click', fetchEmployees);
    addEmployeeBtn.addEventListener('click', showAddEmployeeModal);
    saveBtn.addEventListener('click', saveEmployee);
    deleteBtn.addEventListener('click', showDeleteConfirmation);
    confirmDeleteBtn.addEventListener('click', deleteEmployee);
}

/**
 * Show the dashboard section
 */
function showDashboard() {
    pageTitle.textContent = 'Dashboard';
    dashboardSection.style.display = 'block';
    employeesSection.style.display = 'none';
    
    // Update active nav
    navDashboard.classList.add('active');
    navEmployees.classList.remove('active');
    
    // Refresh dashboard data
    updateDashboardStats();
    renderRecentEmployees();
}

/**
 * Show the employees section
 */
function showEmployees() {
    pageTitle.textContent = 'Employees';
    dashboardSection.style.display = 'none';
    employeesSection.style.display = 'block';
    
    // Update active nav
    navDashboard.classList.remove('active');
    navEmployees.classList.add('active');
    
    // Refresh employees table
    renderEmployeesTable();
}

/**
 * Fetch all employees from the API
 */
async function fetchEmployees() {
    try {
        const response = await fetch(EMPLOYEES_API);
        
        // Check if unauthorized (session expired)
        if (response.status === 401) {
            // Redirect to login
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            employees = data.employees || [];
            
            // Update UI with new data
            updateDashboardStats();
            renderRecentEmployees();
            renderEmployeesTable();
        } else {
            console.error('Error fetching employees:', data.error);
            alert('Failed to load employees. Please try again.');
        }
    } catch (error) {
        console.error('Error fetching employees:', error);
        alert('Failed to load employees. Please check your connection.');
    }
}

/**
 * Update the dashboard statistics
 */
function updateDashboardStats() {
    if (!employees) return;
    
    // Total employees
    totalEmployeesEl.textContent = employees.length;
    
    // Count departments (unique)
    const departments = new Set(employees.map(emp => emp.department));
    totalDepartmentsEl.textContent = departments.size;
    
    // Recent employees (added in the last 7 days)
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    
    const recentCount = employees.filter(emp => {
        const createdAt = new Date(emp.created_at);
        return createdAt >= oneWeekAgo;
    }).length;
    
    recentEmployeesEl.textContent = recentCount;
    
    // Completed onboarding
    const completedCount = employees.filter(emp => 
        emp.status === 'Complete' || emp.status === 'Completed'
    ).length;
    
    completedOnboardingEl.textContent = completedCount;
}

/**
 * Render the recent employees table on the dashboard
 */
function renderRecentEmployees() {
    const tableBody = document.getElementById('recent-employees-body');
    tableBody.innerHTML = '';
    
    if (!employees || employees.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">No employees found</td>
            </tr>
        `;
        return;
    }
    
    // Sort by created date (newest first) and take 5
    const recentEmployees = [...employees]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    
    recentEmployees.forEach(emp => {
        const row = document.createElement('tr');
        
        // Format status as a badge
        const statusClass = getStatusClass(emp.status);
        
        row.innerHTML = `
            <td>${emp.name}</td>
            <td>${emp.position}</td>
            <td>${emp.department}</td>
            <td>${formatDate(emp.startDate)}</td>
            <td><span class="badge ${statusClass}">${emp.status || 'New'}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Render the full employees table
 */
function renderEmployeesTable() {
    const tableBody = document.getElementById('employees-body');
    tableBody.innerHTML = '';
    
    if (!employees || employees.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">No employees found</td>
            </tr>
        `;
        return;
    }
    
    // Sort by name
    const sortedEmployees = [...employees].sort((a, b) => 
        a.name.localeCompare(b.name)
    );
    
    sortedEmployees.forEach(emp => {
        const row = document.createElement('tr');
        
        // Format status as a badge
        const statusClass = getStatusClass(emp.status);
        
        row.innerHTML = `
            <td>${emp.name}</td>
            <td>${emp.position}</td>
            <td>${emp.department}</td>
            <td>${formatDate(emp.startDate)}</td>
            <td><span class="badge ${statusClass}">${emp.status || 'New'}</span></td>
            <td>
                <button class="btn btn-sm btn-info view-btn" data-id="${emp.id}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-primary edit-btn" data-id="${emp.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-btn" data-id="${emp.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        // Add event listeners to buttons
        row.querySelector('.view-btn').addEventListener('click', () => viewEmployee(emp.id));
        row.querySelector('.edit-btn').addEventListener('click', () => editEmployee(emp.id));
        row.querySelector('.delete-btn').addEventListener('click', () => {
            currentEmployeeId = emp.id;
            deleteModal.show();
        });
        
        tableBody.appendChild(row);
    });
}

/**
 * Show the Add Employee modal
 */
function showAddEmployeeModal() {
    // Reset form
    employeeForm.reset();
    employeeIdField.value = '';
    detailsSection.style.display = 'none';
    currentEmployeeId = null;
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = 'Add New Employee';
    
    // Hide delete button, show save button
    deleteBtn.style.display = 'none';
    saveBtn.textContent = 'Add Employee';
    
    // Show modal
    employeeModal.show();
}

/**
 * View employee details
 */
function viewEmployee(employeeId) {
    const employee = employees.find(e => e.id === employeeId);
    if (!employee) return;
    
    // Fill form with employee data
    fillEmployeeForm(employee);
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = 'Employee Details';
    
    // Display details section
    detailsSection.style.display = 'block';
    
    // Make form read-only
    const formInputs = employeeForm.querySelectorAll('input, select');
    formInputs.forEach(input => input.setAttribute('disabled', 'disabled'));
    
    // Show delete button, hide save button
    deleteBtn.style.display = 'inline-block';
    saveBtn.style.display = 'none';
    
    // Save current employee ID
    currentEmployeeId = employeeId;
    
    // Show modal
    employeeModal.show();
}

/**
 * Edit employee
 */
function editEmployee(employeeId) {
    const employee = employees.find(e => e.id === employeeId);
    if (!employee) return;
    
    // Fill form with employee data
    fillEmployeeForm(employee);
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = 'Edit Employee';
    
    // Display details section
    detailsSection.style.display = 'block';
    
    // Enable form inputs
    const formInputs = employeeForm.querySelectorAll('input, select');
    formInputs.forEach(input => input.removeAttribute('disabled'));
    
    // Show buttons
    deleteBtn.style.display = 'inline-block';
    saveBtn.style.display = 'inline-block';
    saveBtn.textContent = 'Save Changes';
    
    // Save current employee ID
    currentEmployeeId = employeeId;
    
    // Show modal
    employeeModal.show();
}

/**
 * Fill employee form with data
 */
function fillEmployeeForm(employee) {
    // Basic info
    document.getElementById('name').value = employee.name || '';
    document.getElementById('position').value = employee.position || '';
    document.getElementById('department').value = employee.department || '';
    document.getElementById('startDate').value = formatDateForInput(employee.startDate) || '';
    document.getElementById('employee-id').value = employee.id || '';
    
    // Equipment needs
    const equipmentList = document.getElementById('equipment-list');
    equipmentList.innerHTML = '';
    
    if (employee.equipmentNeeds && employee.equipmentNeeds.length > 0) {
        employee.equipmentNeeds.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            equipmentList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No equipment needs specified';
        equipmentList.appendChild(li);
    }
    
    // System access
    const accessList = document.getElementById('access-list');
    accessList.innerHTML = '';
    
    if (employee.systemAccess && employee.systemAccess.length > 0) {
        employee.systemAccess.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            accessList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No system access specified';
        accessList.appendChild(li);
    }
    
    // Training requirements
    const trainingList = document.getElementById('training-list');
    trainingList.innerHTML = '';
    
    if (employee.trainingRequirements && employee.trainingRequirements.length > 0) {
        employee.trainingRequirements.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            trainingList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No training requirements specified';
        trainingList.appendChild(li);
    }
    
    // HR Notes
    const hrNotes = document.getElementById('hr-notes');
    hrNotes.innerHTML = '';
    
    if (employee.hrNotes && employee.hrNotes.length > 0) {
        employee.hrNotes.forEach(note => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = note;
            hrNotes.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No HR notes';
        hrNotes.appendChild(li);
    }
    
    // IT Notes
    const itNotes = document.getElementById('it-notes');
    itNotes.innerHTML = '';
    
    if (employee.itNotes && employee.itNotes.length > 0) {
        employee.itNotes.forEach(note => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = note;
            itNotes.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No IT notes';
        itNotes.appendChild(li);
    }
}

/**
 * Show delete confirmation modal
 */
function showDeleteConfirmation() {
    employeeModal.hide();
    deleteModal.show();
}

/**
 * Save employee (create or update)
 */
async function saveEmployee() {
    // Get form data
    const employeeData = {
        name: document.getElementById('name').value,
        position: document.getElementById('position').value,
        department: document.getElementById('department').value,
        startDate: document.getElementById('startDate').value
    };
    
    // Validate form
    if (!employeeData.name || !employeeData.position || !employeeData.department || !employeeData.startDate) {
        alert('Please fill out all required fields');
        return;
    }
    
    try {
        let response;
        
        if (currentEmployeeId) {
            // Update existing employee
            response = await fetch(`${EMPLOYEES_API}/${currentEmployeeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(employeeData)
            });
        } else {
            // Create new employee
            response = await fetch(EMPLOYEES_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(employeeData)
            });
        }
        
        // Check if unauthorized (session expired)
        if (response.status === 401) {
            alert('Your session has expired. Please login again.');
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            // Close modal
            employeeModal.hide();
            
            // Refresh data
            fetchEmployees();
            
            // Show success notification
            alert(currentEmployeeId ? 'Employee updated successfully' : 'Employee added successfully');
        } else {
            console.error('Error saving employee:', data.error);
            alert(`Failed to save employee: ${data.error}`);
        }
    } catch (error) {
        console.error('Error saving employee:', error);
        alert('Failed to save employee. Please check your connection.');
    }
}

/**
 * Delete employee
 */
async function deleteEmployee() {
    if (!currentEmployeeId) {
        deleteModal.hide();
        return;
    }
    
    try {
        const response = await fetch(`${EMPLOYEES_API}/${currentEmployeeId}`, {
            method: 'DELETE'
        });
        
        // Check if unauthorized (session expired)
        if (response.status === 401) {
            alert('Your session has expired. Please login again.');
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            // Close modals
            deleteModal.hide();
            
            // Refresh data
            fetchEmployees();
            
            // Show success notification
            alert('Employee deleted successfully');
        } else {
            console.error('Error deleting employee:', data.error);
            alert(`Failed to delete employee: ${data.error}`);
        }
    } catch (error) {
        console.error('Error deleting employee:', error);
        alert('Failed to delete employee. Please check your connection.');
    }
}

/**
 * Utility function to format date
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    } catch (e) {
        return dateString;
    }
}

/**
 * Format date for input field (YYYY-MM-DD)
 */
function formatDateForInput(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        return date.toISOString().split('T')[0];
    } catch (e) {
        return dateString;
    }
}

/**
 * Get appropriate status class for badges
 */
function getStatusClass(status) {
    if (!status) return 'bg-secondary';
    
    switch (status.toLowerCase()) {
        case 'complete':
        case 'completed':
            return 'bg-success';
        case 'in progress':
            return 'bg-info';
        case 'pending':
            return 'bg-warning';
        default:
            return 'bg-secondary';
    }
}

// Initialize dashboard on load
showDashboard(); 