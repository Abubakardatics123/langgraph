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
const employeeIdField = document.getElementById('employee-id');
const detailsSection = document.getElementById('details-section');
const saveBtn = document.getElementById('save-btn');
const deleteBtn = document.getElementById('delete-btn');
const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

// API endpoints
const API_URL = '/api';
const EMPLOYEES_API = `${API_URL}/admin/employees`;
const AUTH_CHECK_API = `${API_URL}/admin/check-auth`;

// Global state
let employees = [];
let currentEmployeeId = null;
const DEBUG = true; // Enable debugging

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    console.log("Document loaded. Starting employee management initialization...");
    
    // Add direct API test button to help debug
    const refreshBtn = document.getElementById('refresh-btn');
    const directApiBtn = document.createElement('button');
    directApiBtn.className = 'btn btn-sm btn-warning ms-2';
    directApiBtn.innerHTML = '<i class="fas fa-bug"></i> Debug API';
    directApiBtn.onclick = testDirectApiAccess;
    if (refreshBtn && refreshBtn.parentNode) {
        refreshBtn.parentNode.appendChild(directApiBtn);
    }
    
    // Add a direct fetch button for testing
    const directFetchBtn = document.createElement('button');
    directFetchBtn.className = 'btn btn-sm btn-success ms-2';
    directFetchBtn.innerHTML = '<i class="fas fa-database"></i> Direct Fetch';
    directFetchBtn.onclick = directFetchEmployees;
    if (refreshBtn && refreshBtn.parentNode) {
        refreshBtn.parentNode.appendChild(directFetchBtn);
    }
    
    // Initialize the system - try to load data without auth check first
    initializeSystem();
});

/**
 * Initialize the system with data
 */
async function initializeSystem() {
    try {
        console.log("DEBUG: Initializing system...");
        
        // Try direct fetch first
        await directFetchEmployees();
        
        // If that worked, we're done
        if (employees && employees.length > 0) {
            console.log("DEBUG: Direct fetch successful, skipping authentication");
            setupEventListeners();
            return;
        }
        
        // Otherwise fall back to normal auth flow
        const isAuthenticated = await checkAuthentication();
        if (isAuthenticated) {
            console.log("DEBUG: Authentication successful, fetching employees");
            await fetchEmployees();
            setupEventListeners();
        } else {
            console.error("DEBUG: Authentication failed");
            window.location.href = '/login';
        }
    } catch (error) {
        console.error("Error initializing system:", error);
        alert("There was an error initializing the system. Please check the console for details.");
    }
}

/**
 * Direct fetch employees without auth check
 */
async function directFetchEmployees() {
    try {
        console.log('DEBUG: Direct fetching employees...');
        
        const response = await fetch(EMPLOYEES_API, {
            method: 'GET',
            credentials: 'include',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('Direct fetch error:', response.status);
            return false;
        }
        
        const data = await response.json();
        console.log('Direct fetch data:', data);
        
        if (data && data.employees) {
            employees = data.employees || [];
            console.log(`Loaded ${employees.length} employees directly`);
            renderEmployeesTable();
            return true;
        } else {
            console.error('Invalid API response format in direct fetch');
            return false;
        }
    } catch (error) {
        console.error('Error in direct fetch:', error);
        return false;
    }
}

/**
 * Test direct API access without fetch
 */
function testDirectApiAccess() {
    console.log("Testing direct API access...");
    
    // Create a modal to show the response
    const modalContainer = document.createElement('div');
    modalContainer.className = 'modal fade';
    modalContainer.id = 'apiDebugModal';
    modalContainer.setAttribute('tabindex', '-1');
    
    modalContainer.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-warning">
                    <h5 class="modal-title">API Debug Response</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-3" id="debug-loading">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Loading API response...</p>
                    </div>
                    <pre id="debug-response" style="max-height: 400px; overflow: auto;"></pre>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const debugModal = new bootstrap.Modal(document.getElementById('apiDebugModal'));
    debugModal.show();
    
    // Make the API request directly via XHR to avoid fetch complexities
    const xhr = new XMLHttpRequest();
    xhr.open('GET', EMPLOYEES_API);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.withCredentials = true;
    
    xhr.onload = function() {
        const debugLoading = document.getElementById('debug-loading');
        const debugResponse = document.getElementById('debug-response');
        
        if (debugLoading) debugLoading.style.display = 'none';
        
        if (xhr.status === 200) {
            // Pretty-print the JSON response
            try {
                const data = JSON.parse(xhr.responseText);
                if (debugResponse) {
                    debugResponse.textContent = JSON.stringify(data, null, 2);
                }
                console.log('Debug API response:', data);
            } catch (e) {
                if (debugResponse) {
                    debugResponse.textContent = xhr.responseText;
                }
                console.error('Error parsing JSON:', e);
            }
        } else {
            if (debugResponse) {
                debugResponse.textContent = `Error ${xhr.status}: ${xhr.statusText}\n\n${xhr.responseText}`;
                debugResponse.className = 'text-danger';
            }
            console.error('Debug API error:', xhr.status, xhr.statusText);
        }
    };
    
    xhr.onerror = function() {
        const debugLoading = document.getElementById('debug-loading');
        const debugResponse = document.getElementById('debug-response');
        
        if (debugLoading) debugLoading.style.display = 'none';
        if (debugResponse) {
            debugResponse.textContent = 'Network error occurred while fetching data.';
            debugResponse.className = 'text-danger';
        }
        console.error('Debug API network error');
    };
    
    xhr.send();
}

/**
 * Check if the user is authenticated
 */
async function checkAuthentication() {
    try {
        console.log("DEBUG: Starting authentication check");
        if (DEBUG) console.log("Checking authentication at:", AUTH_CHECK_API);
        
        const response = await fetch(AUTH_CHECK_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (DEBUG) console.log("Auth check response:", response.status);
        
        if (response.ok) {
            const data = await response.json();
            if (DEBUG) console.log("Auth check data:", data);
            console.log("DEBUG: Authentication successful");
            return true;
        } else {
            console.error("Authentication check failed:", response.status);
            // Try logging in automatically for debugging
            if (DEBUG) {
                console.log("Debug mode: Attempting auto-login");
                const loginResponse = await fetch('/api/admin/login', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: 'admin',
                        password: 'password123'
                    })
                });
                
                if (loginResponse.ok) {
                    console.log("DEBUG: Auto-login successful");
                    return true;
                } else {
                    console.log("DEBUG: Auto-login failed:", await loginResponse.text());
                }
            }
            return false;
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
        return false;
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Buttons
    refreshBtn.addEventListener('click', fetchEmployees);
    addEmployeeBtn.addEventListener('click', showAddEmployeeModal);
    saveBtn.addEventListener('click', saveEmployee);
    deleteBtn.addEventListener('click', showDeleteConfirmation);
    confirmDeleteBtn.addEventListener('click', deleteEmployee);
}

/**
 * Fetch all employees from the API
 */
async function fetchEmployees() {
    try {
        console.log('DEBUG: Starting fetchEmployees');
        console.log('Fetching employees from:', EMPLOYEES_API);
        
        // Use credentials to send cookies
        const response = await fetch(EMPLOYEES_API, {
            method: 'GET',
            credentials: 'include', // Important for sending cookies
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        // Check if unauthorized (session expired)
        if (response.status === 401) {
            console.error('Authentication error: Unauthorized');
            alert('Your session has expired. Please login again.');
            // Redirect to login
            window.location.href = '/login';
            return;
        }
        
        // Check for other error responses
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error ${response.status}: ${errorText}`);
            throw new Error(`Server returned ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('API response data:', data);
        
        if (data && data.employees) {
            employees = data.employees || [];
            console.log(`Loaded ${employees.length} employees:`, employees);
            
            // Update UI with new data
            renderEmployeesTable();
        } else {
            console.error('Invalid API response format:', data);
            alert('Received invalid data format from server');
        }
    } catch (error) {
        console.error('Error fetching employees:', error);
        alert('Failed to load employees. Error: ' + error.message);
    }
}

/**
 * Render the employees table
 */
function renderEmployeesTable() {
    console.log('DEBUG: Rendering employees table');
    const tableBody = document.getElementById('employees-body');
    if (!tableBody) {
        console.error('ERROR: Could not find employees-body element');
        return;
    }
    
    tableBody.innerHTML = '';
    
    if (!employees || employees.length === 0) {
        console.log('DEBUG: No employees to display');
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">No employees found</td>
            </tr>
        `;
        return;
    }
    
    console.log(`DEBUG: Rendering ${employees.length} employees`);
    
    try {
        // Sort by name, handling missing name values
        const sortedEmployees = [...employees].sort((a, b) => {
            if (!a.name) return 1;
            if (!b.name) return -1;
            return a.name.localeCompare(b.name);
        });
        
        sortedEmployees.forEach((emp, index) => {
            try {
                const row = document.createElement('tr');
                
                // Format status as a badge
                const statusClass = getStatusClass(emp.status);
                
                row.innerHTML = `
                    <td>${emp.name || 'N/A'}</td>
                    <td>${emp.position || 'N/A'}</td>
                    <td>${emp.department || 'N/A'}</td>
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
                const viewBtn = row.querySelector('.view-btn');
                const editBtn = row.querySelector('.edit-btn');
                const deleteBtn = row.querySelector('.delete-btn');
                
                if (viewBtn) viewBtn.addEventListener('click', () => viewEmployee(emp.id));
                if (editBtn) editBtn.addEventListener('click', () => editEmployee(emp.id));
                if (deleteBtn) deleteBtn.addEventListener('click', () => {
                    currentEmployeeId = emp.id;
                    deleteModal.show();
                });
                
                tableBody.appendChild(row);
                console.log(`DEBUG: Added employee row ${index+1}: ${emp.name}`);
            } catch (rowError) {
                console.error(`Error rendering employee row ${index}:`, rowError, emp);
            }
        });
    } catch (error) {
        console.error('Error rendering employees table:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    Error rendering employees. See console for details.
                </td>
            </tr>
        `;
    }
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
    saveBtn.style.display = 'inline-block';
    saveBtn.textContent = 'Add Employee';
    
    // Make form editable
    const formInputs = employeeForm.querySelectorAll('input, select');
    formInputs.forEach(input => input.removeAttribute('disabled'));
    
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
    
    // Equipment needs
    const equipmentList = document.getElementById('equipment-list');
    equipmentList.innerHTML = '';
    
    if (employee.equipmentNeeds && Array.isArray(employee.equipmentNeeds) && employee.equipmentNeeds.length > 0) {
        employee.equipmentNeeds.forEach(item => {
            if (!item) return; // Skip null/undefined items
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
    
    if (employee.systemAccess && Array.isArray(employee.systemAccess) && employee.systemAccess.length > 0) {
        employee.systemAccess.forEach(item => {
            if (!item) return; // Skip null/undefined items
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
    
    if (employee.trainingRequirements && Array.isArray(employee.trainingRequirements) && employee.trainingRequirements.length > 0) {
        employee.trainingRequirements.forEach(item => {
            if (!item) return; // Skip null/undefined items
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
    
    if (employee.hrNotes && Array.isArray(employee.hrNotes) && employee.hrNotes.length > 0) {
        employee.hrNotes.forEach(note => {
            if (!note) return; // Skip null/undefined items
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
    
    if (employee.itNotes && Array.isArray(employee.itNotes) && employee.itNotes.length > 0) {
        employee.itNotes.forEach(note => {
            if (!note) return; // Skip null/undefined items
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
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(employeeData)
            });
        } else {
            // Create new employee
            response = await fetch(EMPLOYEES_API, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
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
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
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