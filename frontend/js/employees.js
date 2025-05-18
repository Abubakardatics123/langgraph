/**
 * HR Workflow Employees Page JavaScript
 * Handles all the employee management functionality
 */

// DOM References
const refreshBtn = document.getElementById('refresh-btn');
const addEmployeeBtn = document.getElementById('add-employee-btn');

// Employee form elements
const employeeForm = document.getElementById('employee-form');
const employeeModal = new bootstrap.Modal(document.getElementById('employeeModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
const completeModal = new bootstrap.Modal(document.getElementById('confirmCompleteModal'));
const employeeIdField = document.getElementById('employee-id');
const detailsSection = document.getElementById('details-section');
const saveBtn = document.getElementById('save-btn');
const deleteBtn = document.getElementById('delete-btn');
const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
const completeOnboardingBtn = document.getElementById('complete-onboarding-btn');
const confirmCompleteBtn = document.getElementById('confirm-complete-btn');
const refreshPendingBtn = document.getElementById('refresh-pending-btn');

// Tab references
const allEmployeesTab = document.getElementById('all-employees-tab');
const pendingEmployeesTab = document.getElementById('pending-employees-tab');
const pendingCount = document.getElementById('pending-count');

// API endpoints
const API_BASE_URL = '/api';
const EMPLOYEES_API = `${API_BASE_URL}/admin/employees`;
const PENDING_EMPLOYEES_API = `${API_BASE_URL}/admin/employees/pending`;
const COMPLETE_ONBOARDING_API = `${API_BASE_URL}/admin/employees/complete-onboarding`;
const AUTH_CHECK_API = `${API_BASE_URL}/admin/check-auth`;

// Global state
let employees = [];
let pendingEmployees = [];
let currentEmployeeId = null;
let currentTab = 'all'; // 'all' or 'pending'
const DEBUG = true; // Enable debugging

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing employees page...");
    
    // Check authentication
    checkAuthentication().then(isAuthenticated => {
        if (isAuthenticated) {
            initializePage();
        } else {
            window.location.href = '/login';
        }
    });
});

/**
 * Check if the user is authenticated
 */
async function checkAuthentication() {
    try {
        const response = await fetch(AUTH_CHECK_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.authenticated;
        }
        return false;
    } catch (error) {
        console.error('Error checking authentication:', error);
        return false;
    }
}

/**
 * Initialize the page
 */
function initializePage() {
    // Set up event listeners for tabs
    allEmployeesTab.addEventListener('click', () => {
        currentTab = 'all';
        if (employees.length === 0) {
            fetchEmployees();
        }
    });
    
    pendingEmployeesTab.addEventListener('click', () => {
        currentTab = 'pending';
        fetchPendingEmployees();
    });
    
    // Set up event listeners
    document.getElementById('refresh-btn').addEventListener('click', fetchEmployees);
    document.getElementById('refresh-pending-btn').addEventListener('click', fetchPendingEmployees);
    document.getElementById('add-employee-btn').addEventListener('click', showAddEmployeeModal);
    document.getElementById('save-btn').addEventListener('click', saveEmployee);
    document.getElementById('delete-btn').addEventListener('click', showDeleteConfirmation);
    document.getElementById('confirm-delete-btn').addEventListener('click', deleteEmployee);
    document.getElementById('complete-onboarding-btn').addEventListener('click', showCompleteOnboardingConfirmation);
    document.getElementById('confirm-complete-btn').addEventListener('click', completeOnboarding);
    document.getElementById('logout-btn')?.addEventListener('click', logout);
    
    // Initialize the employee list
    fetchEmployees();
}

/**
 * Fetch all employees from the API
 */
async function fetchEmployees() {
    try {
        document.getElementById('employees-body').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p>Loading employees...</p>
                </td>
            </tr>
        `;
        
        const response = await fetch(EMPLOYEES_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Unauthorized - redirect to login
                window.location.href = '/login';
                return;
            }
            throw new Error(`Server returned ${response.status}: ${await response.text()}`);
        }
        
        const data = await response.json();
        
        if (data && Array.isArray(data.employees)) {
            employees = data.employees;
            renderEmployeesTable();
            
            // Also fetch pending employees to update the counter
            fetchPendingEmployees(false);
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error fetching employees:', error);
        document.getElementById('employees-body').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error loading employees: ${error.message}
                </td>
            </tr>
        `;
    }
}

/**
 * Fetch pending employees from the API
 */
async function fetchPendingEmployees(renderTable = true) {
    try {
        if (renderTable) {
            document.getElementById('pending-body').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Loading pending employees...</p>
                    </td>
                </tr>
            `;
        }
        
        const response = await fetch(PENDING_EMPLOYEES_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Unauthorized - redirect to login
                window.location.href = '/login';
                return;
            }
            throw new Error(`Server returned ${response.status}: ${await response.text()}`);
        }
        
        const data = await response.json();
        
        if (data && Array.isArray(data.employees)) {
            pendingEmployees = data.employees;
            
            // Update the counter badge
            pendingCount.textContent = pendingEmployees.length;
            
            // Only render if we're on the pending tab or explicitly requested
            if (renderTable) {
                renderPendingEmployeesTable();
            }
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error fetching pending employees:', error);
        if (renderTable) {
            document.getElementById('pending-body').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle"></i> Error loading pending employees: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Render the employees table
 */
function renderEmployeesTable() {
    const tableBody = document.getElementById('employees-body');
    
    if (!employees || employees.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <i class="fas fa-users me-2"></i>No employees found
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = '';
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        
        // Format date
        const formattedDate = formatDate(employee.startDate);
        
        // Get status class
        const statusClass = getStatusClass(employee.status);
        
        row.innerHTML = `
            <td>${employee.name || 'N/A'}</td>
            <td>${employee.position || 'N/A'}</td>
            <td>${employee.department || 'N/A'}</td>
            <td>${formattedDate}</td>
            <td><span class="badge ${statusClass}">${employee.status || 'New'}</span></td>
            <td class="text-center">
                <div class="btn-group">
                    <button class="btn btn-sm btn-info view-btn" data-id="${employee.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-primary edit-btn" data-id="${employee.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-btn" data-id="${employee.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to buttons
    addTableButtonListeners('employees-body');
}

/**
 * Render the pending employees table
 */
function renderPendingEmployeesTable() {
    const tableBody = document.getElementById('pending-body');
    
    if (!pendingEmployees || pendingEmployees.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <i class="fas fa-check-circle me-2 text-success"></i>No pending onboarding employees
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = '';
    
    pendingEmployees.forEach(employee => {
        const row = document.createElement('tr');
        
        // Format date
        const formattedDate = formatDate(employee.startDate);
        
        // Get status class
        const statusClass = getStatusClass(employee.status);
        
        row.innerHTML = `
            <td>${employee.name || 'N/A'}</td>
            <td>${employee.position || 'N/A'}</td>
            <td>${employee.department || 'N/A'}</td>
            <td>${formattedDate}</td>
            <td><span class="badge ${statusClass}">${employee.status || 'New'}</span></td>
            <td class="text-center">
                <div class="btn-group">
                    <button class="btn btn-sm btn-info view-btn" data-id="${employee.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-success complete-btn" data-id="${employee.id}" title="Complete Onboarding">
                        <i class="fas fa-check-circle"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to buttons
    addTableButtonListeners('pending-body');
}

/**
 * Add event listeners to table buttons
 */
function addTableButtonListeners(tableId) {
    const tableBody = document.getElementById(tableId);
    
    // View buttons
    tableBody.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            viewEmployee(id);
        });
    });
    
    // Edit buttons
    tableBody.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            editEmployee(id);
        });
    });
    
    // Delete buttons
    tableBody.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            currentEmployeeId = id;
            showDeleteConfirmation();
        });
    });
    
    // Complete onboarding buttons
    tableBody.querySelectorAll('.complete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            currentEmployeeId = id;
            showCompleteOnboardingConfirmation();
        });
    });
}

/**
 * Get the appropriate Bootstrap class for a status
 */
function getStatusClass(status) {
    switch (status ? status.toLowerCase() : '') {
        case 'completed':
            return 'bg-success';
        case 'in progress':
        case 'onboarding':
            return 'bg-primary';
        case 'pending':
            return 'bg-warning';
        case 'error':
        case 'failed':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

/**
 * Shows the modal for adding a new employee
 */
function showAddEmployeeModal() {
    // Navigate to the dedicated new employee page
    window.location.href = '/admin/employees/new';
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = 'Add New Employee';
    
    // Hide the delete button for new employees
    document.getElementById('delete-btn').style.display = 'none';
    
    // Show save button with appropriate text
    const saveBtn = document.getElementById('save-btn');
    saveBtn.style.display = 'inline-block';
    saveBtn.textContent = 'Create Employee';
    
    // Enable form fields
    enableFormFields();
    
    // Show the modal
    const employeeModal = new bootstrap.Modal(document.getElementById('employeeModal'));
    employeeModal.show();
}

/**
 * View employee details
 */
function viewEmployee(employeeId) {
    // Find the employee in the appropriate array
    let employee;
    if (currentTab === 'all') {
        employee = employees.find(emp => emp.id === employeeId);
    } else {
        employee = pendingEmployees.find(emp => emp.id === employeeId);
    }
    
    if (!employee) {
        console.error('Employee not found:', employeeId);
        return;
    }
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = `${employee.name} - Details`;
    
    // Fill the form with employee data
    fillEmployeeForm(employee);
    
    // Disable form fields for view mode
    disableFormFields();
    
    // Hide save button, show appropriate action buttons
    saveBtn.style.display = 'none';
    deleteBtn.style.display = 'inline-block';
    
    // Show complete onboarding button for pending employees
    const isPending = ['pending', 'new', 'in progress', 'onboarding'].includes(
        (employee.status || '').toLowerCase()
    );
    completeOnboardingBtn.style.display = isPending ? 'inline-block' : 'none';
    
    // Set the current employee ID
    currentEmployeeId = employeeId;
    
    // Show the modal
    employeeModal.show();
}

/**
 * Edit employee
 */
function editEmployee(employeeId) {
    // Find the employee in the appropriate array
    let employee;
    if (currentTab === 'all') {
        employee = employees.find(emp => emp.id === employeeId);
    } else {
        employee = pendingEmployees.find(emp => emp.id === employeeId);
    }
    
    if (!employee) {
        console.error('Employee not found:', employeeId);
        return;
    }
    
    // Set modal title
    document.getElementById('employeeModalLabel').textContent = `Edit ${employee.name}`;
    
    // Fill the form with employee data
    fillEmployeeForm(employee);
    
    // Enable form fields for edit mode
    enableFormFields();
    
    // Show save button and delete button
    saveBtn.style.display = 'inline-block';
    deleteBtn.style.display = 'inline-block';
    completeOnboardingBtn.style.display = 'none';
    
    // Set the current employee ID
    currentEmployeeId = employeeId;
    
    // Show the modal
    employeeModal.show();
}

/**
 * Enable form fields for editing
 */
function enableFormFields() {
    const formInputs = document.getElementById('employee-form').querySelectorAll('input, select');
    formInputs.forEach(input => input.removeAttribute('disabled'));
}

/**
 * Disable form fields for viewing
 */
function disableFormFields() {
    const formInputs = document.getElementById('employee-form').querySelectorAll('input, select');
    formInputs.forEach(input => input.setAttribute('disabled', 'disabled'));
}

/**
 * Fill employee form with data
 */
function fillEmployeeForm(employee) {
    if (!employee) {
        console.error('No employee data provided');
        return;
    }
    
    // Basic info
    document.getElementById('name').value = employee.name || '';
    document.getElementById('position').value = employee.position || '';
    document.getElementById('department').value = employee.department || '';
    document.getElementById('startDate').value = formatDateForInput(employee.startDate) || '';
    document.getElementById('employee-id').value = employee.id || '';
    
    // Populate lists
    populateList('equipment-list', employee.equipmentNeeds, 'No equipment needs specified');
    populateList('access-list', employee.systemAccess, 'No system access specified');
    populateList('training-list', employee.trainingRequirements, 'No training requirements specified');
    populateList('hr-notes', employee.hrNotes, 'No HR notes');
    populateList('it-notes', employee.itNotes, 'No IT notes');
}

/**
 * Populate a list element with data
 */
function populateList(listId, items, emptyMessage) {
    const listElement = document.getElementById(listId);
    listElement.innerHTML = '';
    
    if (items && Array.isArray(items) && items.length > 0) {
        items.forEach(item => {
            if (!item) return; // Skip null/undefined items
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            listElement.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = emptyMessage;
        listElement.appendChild(li);
    }
}

/**
 * Show delete confirmation modal
 */
function showDeleteConfirmation() {
    if (!currentEmployeeId) {
        alert('No employee selected for deletion');
        return;
    }
    
    // Hide employee modal and show delete confirmation
    const employeeModal = bootstrap.Modal.getInstance(document.getElementById('employeeModal'));
    if (employeeModal) {
        employeeModal.hide();
    }
    
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    confirmModal.show();
}

/**
 * Save the employee data (create or update)
 */
async function saveEmployee() {
    try {
        // Get form data
        const id = document.getElementById('employee-id').value;
        const name = document.getElementById('name').value;
        const position = document.getElementById('position').value;
        const department = document.getElementById('department').value;
        const startDate = document.getElementById('startDate').value;
        
        // Validate form
        if (!name || !position || !department || !startDate) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Prepare employee data
        const employeeData = {
            name,
            position,
            department,
            startDate
        };
        
        // Determine if this is a create or update operation
        const isUpdate = id && id.trim() !== '';
        const url = isUpdate ? `${EMPLOYEES_API}/${id}` : EMPLOYEES_API;
        const method = isUpdate ? 'PUT' : 'POST';
        
        // Show loading indicator
        const saveBtn = document.getElementById('save-btn');
        const originalText = saveBtn.textContent;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        saveBtn.disabled = true;
        
        // Send API request
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(employeeData)
        });
        
        // Reset button state
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error (${response.status}): ${errorText}`);
        }
        
        const result = await response.json();
        
        // Hide modal
        const employeeModal = bootstrap.Modal.getInstance(document.getElementById('employeeModal'));
        if (employeeModal) {
            employeeModal.hide();
        }
        
        // Refresh employee list
        await fetchEmployees();
        
        // Show success notification
        showNotification(isUpdate ? 'Employee updated successfully!' : 'Employee created successfully!', 'success');
        
    } catch (error) {
        console.error('Error saving employee:', error);
        showNotification(`Error saving employee: ${error.message}`, 'danger');
    }
}

/**
 * Delete the employee
 */
async function deleteEmployee() {
    if (!currentEmployeeId) {
        showNotification('No employee selected for deletion', 'warning');
        return;
    }
    
    try {
        // Show loading indicator
        const deleteBtn = document.getElementById('confirm-delete-btn');
        deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
        deleteBtn.disabled = true;
        
        // Send delete request
        const response = await fetch(`${EMPLOYEES_API}/${currentEmployeeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Reset button state
        deleteBtn.innerHTML = 'Delete';
        deleteBtn.disabled = false;
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error (${response.status}): ${errorText}`);
        }
        
        // Hide confirm modal
        const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        if (confirmModal) {
            confirmModal.hide();
        }
        
        // Refresh employee list
        await fetchEmployees();
        
        // Reset current employee ID
        currentEmployeeId = null;
        
        // Show success notification
        showNotification('Employee deleted successfully!', 'success');
        
    } catch (error) {
        console.error('Error deleting employee:', error);
        showNotification(`Error deleting employee: ${error.message}`, 'danger');
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add notification to the document
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

/**
 * Logout function
 */
async function logout() {
    try {
        await fetch('/api/admin/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/login';
    } catch (error) {
        console.error('Error during logout:', error);
        window.location.href = '/login';
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return dateString;
        }
        return date.toLocaleDateString();
    } catch (e) {
        console.warn('Error formatting date:', e);
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
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return '';
        }
        
        // Format as YYYY-MM-DD
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    } catch (e) {
        console.warn('Error formatting date for input:', e);
        return '';
    }
}

/**
 * Show the confirmation modal for completing onboarding
 */
function showCompleteOnboardingConfirmation() {
    completeModal.show();
}

/**
 * Complete an employee's onboarding process
 */
async function completeOnboarding() {
    if (!currentEmployeeId) {
        console.error('No employee selected');
        return;
    }
    
    try {
        const response = await fetch(`${COMPLETE_ONBOARDING_API}/${currentEmployeeId}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${await response.text()}`);
        }
        
        const data = await response.json();
        
        // Close modals
        completeModal.hide();
        employeeModal.hide();
        
        // Show notification
        showNotification(`Onboarding completed for ${data.employee.name}`, 'success');
        
        // Refresh both tables
        fetchEmployees();
        fetchPendingEmployees();
    } catch (error) {
        console.error('Error completing onboarding:', error);
        showNotification(`Error completing onboarding: ${error.message}`, 'danger');
    }
} 