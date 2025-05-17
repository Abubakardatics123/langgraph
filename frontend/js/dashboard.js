/**
 * HR Workflow Dashboard JavaScript
 * Handles the dashboard functionality
 */

// DOM References
const totalEmployeesEl = document.getElementById('total-employees');
const totalDepartmentsEl = document.getElementById('total-departments');
const recentEmployeesEl = document.getElementById('recent-employees');
const completedOnboardingEl = document.getElementById('completed-onboarding');
const recentEmployeesBody = document.getElementById('recent-employees-body');
const refreshBtn = document.getElementById('refresh-btn');
const addEmployeeBtn = document.getElementById('add-employee-btn');
const logoutBtn = document.getElementById('logout-btn');

// API endpoints
const API_URL = '/api';
const EMPLOYEES_API = `${API_URL}/admin/employees`;
const AUTH_CHECK_API = `${API_URL}/admin/check-auth`;
const LOGOUT_API = `${API_URL}/admin/logout`;

// Global state
let employees = [];
let currentUser = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication first
    checkAuthentication().then(isAuthenticated => {
        if (isAuthenticated) {
            // Fetch initial data
            fetchEmployees();

            // Setup event listeners
            setupEventListeners();
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
        const response = await fetch(AUTH_CHECK_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.username;
            console.log("User authenticated:", currentUser);
            return true;
        } else {
            console.error("Authentication failed:", response.status);
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
    // Refresh button
    if (refreshBtn) {
        refreshBtn.addEventListener('click', fetchEmployees);
    }
    
    // Add employee button
    if (addEmployeeBtn) {
        addEmployeeBtn.addEventListener('click', () => {
            window.location.href = '/admin/employees/new';
        });
    }
    
    // Logout button
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logoutUser);
    }
}

/**
 * Logout user
 */
async function logoutUser() {
    try {
        const response = await fetch(LOGOUT_API, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            console.log("Logout successful");
            // Redirect to login page
            window.location.href = '/login';
        } else {
            console.error('Logout failed:', response.status);
            alert('Failed to logout. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('An error occurred during logout. Please try again.');
    }
}

/**
 * Fetch all employees from the API
 */
async function fetchEmployees() {
    try {
        console.log("Fetching employee data...");
        const response = await fetch(EMPLOYEES_API, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        // Check if unauthorized (session expired)
        if (response.status === 401) {
            console.error("Session expired, redirecting to login");
            // Redirect to login
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            employees = data.employees || [];
            console.log(`Loaded ${employees.length} employees`);
            
            // Update dashboard stats
            updateDashboardStats();
            
            // Render recent employees table
            renderRecentEmployees();
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
    if (totalEmployeesEl) {
        totalEmployeesEl.textContent = employees.length;
    }
    
    // Count departments (unique)
    if (totalDepartmentsEl) {
        // Filter out null, undefined, or empty departments
        const departmentsArray = employees
            .map(emp => emp.department)
            .filter(dept => dept && dept.trim() !== '');
            
        // Count only unique valid departments
        const departments = new Set(departmentsArray);
        totalDepartmentsEl.textContent = departments.size;
    }
    
    // Recent employees (added in the last 7 days)
    if (recentEmployeesEl) {
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        
        const recentCount = employees.filter(emp => {
            if (!emp.created_at) return false;
            const createdAt = new Date(emp.created_at);
            return createdAt >= oneWeekAgo;
        }).length;
        
        recentEmployeesEl.textContent = recentCount;
    }
    
    // Completed onboarding - use case-insensitive matching
    if (completedOnboardingEl) {
        const completedCount = employees.filter(emp => {
            // Handle case when status is null/undefined
            if (!emp.status) return false;
            
            // Case-insensitive matching
            const status = emp.status.toLowerCase();
            return status === 'complete' || status === 'completed';
        }).length;
        
        completedOnboardingEl.textContent = completedCount;
        console.log(`Found ${completedCount} employees with completed status`);
    }
}

/**
 * Render the recent employees table
 */
function renderRecentEmployees() {
    if (!recentEmployeesBody) return;
    
    recentEmployeesBody.innerHTML = '';
    
    if (!employees || employees.length === 0) {
        recentEmployeesBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">No employees found</td>
            </tr>
        `;
        return;
    }
    
    // Sort by created date (newest first) and show all employees
    const sortedEmployees = [...employees]
        .sort((a, b) => {
            // Handle missing created_at values
            if (!a.created_at) return 1;
            if (!b.created_at) return -1;
            return new Date(b.created_at) - new Date(a.created_at);
        });
    
    sortedEmployees.forEach(emp => {
        const row = document.createElement('tr');
        
        // Format status as a badge
        const statusClass = getStatusClass(emp.status);
        
        row.innerHTML = `
            <td>${emp.name || 'N/A'}</td>
            <td>${emp.position || 'N/A'}</td>
            <td>${emp.department || 'N/A'}</td>
            <td>${formatDate(emp.startDate)}</td>
            <td><span class="badge ${statusClass}">${emp.status || 'New'}</span></td>
        `;
        
        recentEmployeesBody.appendChild(row);
    });
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
 * Get appropriate status class for badges
 */
function getStatusClass(status) {
    if (!status) return 'bg-secondary';
    
    // Convert to lowercase for case-insensitive comparison
    const statusLower = status.toLowerCase();
    
    switch (statusLower) {
        case 'complete':
        case 'completed':
            return 'bg-success';
        case 'in progress':
        case 'inprogress':
        case 'in-progress':
            return 'bg-info';
        case 'pending':
        case 'new':
        case 'waiting':
            return 'bg-warning';
        default:
            console.log(`Unknown status value: ${status}`);
            return 'bg-secondary';
    }
} 