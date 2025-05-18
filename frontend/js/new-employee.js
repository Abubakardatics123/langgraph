// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const newEmployeeForm = document.getElementById('new-employee-form');
    const cancelBtn = document.getElementById('cancel-btn');
    
    // Form submission
    newEmployeeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(newEmployeeForm);
        const employeeData = {
            name: formData.get('name'),
            email: formData.get('email'),
            position: formData.get('position'),
            department: formData.get('department'),
            startDate: formData.get('startDate'),
            manager: formData.get('manager'),
            notes: formData.get('notes'),
            equipment: getCheckboxValues('equipment[]'),
            access: getCheckboxValues('access[]'),
            status: 'pending'
        };
        
        // Submit to API
        createEmployee(employeeData);
    });
    
    // Cancel button - return to employees page
    cancelBtn.addEventListener('click', function() {
        window.location.href = '/admin/employees';
    });
    
    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Perform logout actions here
            fetch('/api/admin/logout', {
                method: 'POST',
                credentials: 'include'
            })
            .then(() => {
                window.location.href = '/login';
            })
            .catch(error => {
                console.error('Error logging out:', error);
                window.location.href = '/login';
            });
        });
    }
    
    // Helper function to get checkbox values
    function getCheckboxValues(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
        return Array.from(checkboxes).map(cb => cb.value);
    }
    
    // Create new employee via API
    async function createEmployee(employeeData) {
        try {
            const response = await fetch('/api/admin/employees', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(employeeData)
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Show success message
            alert('Employee created successfully!');
            
            // Redirect to employees list
            window.location.href = '/admin/employees';
        } catch (error) {
            console.error('Error creating employee:', error);
            alert('Failed to create employee. Please try again.');
        }
    }
}); 