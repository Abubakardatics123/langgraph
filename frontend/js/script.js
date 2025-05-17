// HR Onboarding Workflow Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const form = document.getElementById('onboarding-form');
    const employeeFormSection = document.getElementById('employee-form');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const restartBtn = document.getElementById('restart-btn');
    const errorRetryBtn = document.getElementById('error-retry-btn');
    const progressBar = document.getElementById('progress-bar');
    
    // API endpoint
    const apiBaseUrl = 'http://localhost:5000';
    const apiEndpoint = apiBaseUrl + '/api/start-onboarding';
    
    // Check API health on page load
    checkApiHealth();
    
    // Form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        startOnboarding();
    });
    
    // Restart button handler
    restartBtn.addEventListener('click', function() {
        resetUI();
    });
    
    // Error retry button handler
    errorRetryBtn.addEventListener('click', function() {
        resetUI();
    });
    
    // Function to check API health
    function checkApiHealth() {
        fetch(apiBaseUrl + '/api/health')
            .then(response => response.json())
            .then(data => {
                if (!data.workflow_ready) {
                    showError('Workflow system is not ready. Please try again later.', 
                             'The workflow could not be initialized. This might be due to issues with the Groq API connection or Python environment.');
                }
            })
            .catch(error => {
                console.error('Health check failed:', error);
                showError('Cannot connect to API. Please make sure the server is running.',
                         'Detailed error: ' + error.message);
            });
    }
    
    // Function to start the onboarding process
    function startOnboarding() {
        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            position: document.getElementById('position').value,
            department: document.getElementById('department').value,
            startDate: document.getElementById('startDate').value
        };
        
        // Show loading UI
        employeeFormSection.classList.add('d-none');
        loadingSection.classList.remove('d-none');
        
        // Simulate progress bar
        simulateProgress();
        
        // Call API
        fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                // Get the content type
                const contentType = response.headers.get('content-type');
                // If the response is JSON, parse it for more details
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(errorData => {
                        throw new Error(JSON.stringify(errorData));
                    });
                } else {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
            }
            return response.json();
        })
        .then(data => {
            // Complete progress bar
            progressBar.style.width = '100%';
            
            // Delay to show the completed progress bar
            setTimeout(() => {
                // Hide loading screen
                loadingSection.classList.add('d-none');
                
                // Display results
                displayResults(data);
                
                // Show results screen
                resultsSection.classList.remove('d-none');
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingSection.classList.add('d-none');
            
            let errorMsg = 'Error processing onboarding: ' + error.message;
            let detailMsg = '';
            
            // Try to parse the error message if it's JSON
            try {
                const errorData = JSON.parse(error.message);
                errorMsg = `Error: ${errorData.error}`;
                if (errorData.error_type) {
                    errorMsg += ` (${errorData.error_type})`;
                }
                if (errorData.details) {
                    detailMsg = errorData.details;
                }
            } catch (e) {
                // Not JSON, use the error message as is
            }
            
            showError(errorMsg, detailMsg);
        });
    }
    
    // Function to display results
    function displayResults(data) {
        // Set employee info
        document.getElementById('result-name').textContent = data.employee.name;
        document.getElementById('result-position').textContent = data.employee.position;
        document.getElementById('result-department').textContent = data.employee.department;
        document.getElementById('result-startDate').textContent = formatDate(data.employee.startDate);
        
        // Set equipment list
        const equipmentList = document.getElementById('equipment-list');
        equipmentList.innerHTML = '';
        data.employee.equipmentNeeds.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            equipmentList.appendChild(li);
        });
        
        // Set access list
        const accessList = document.getElementById('access-list');
        accessList.innerHTML = '';
        data.employee.systemAccess.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            accessList.appendChild(li);
        });
        
        // Set training list
        const trainingList = document.getElementById('training-list');
        trainingList.innerHTML = '';
        data.employee.trainingRequirements.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = item;
            trainingList.appendChild(li);
        });
        
        // Set HR notes
        const hrNotes = document.getElementById('hr-notes');
        hrNotes.innerHTML = '';
        data.hrNotes.forEach(note => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa fa-check-circle text-success"></i> ${note}`;
            hrNotes.appendChild(li);
        });
        
        // Set IT notes
        const itNotes = document.getElementById('it-notes');
        itNotes.innerHTML = '';
        data.itNotes.forEach(note => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa fa-check-circle text-success"></i> ${note}`;
            itNotes.appendChild(li);
        });
    }
    
    // Function to show error
    function showError(message, details = '') {
        errorMessage.innerHTML = message;
        
        // Add details if provided
        if (details) {
            const detailsPara = document.createElement('div');
            detailsPara.className = 'mt-3 p-2 bg-light border rounded small';
            detailsPara.style.maxHeight = '200px';
            detailsPara.style.overflowY = 'auto';
            detailsPara.innerHTML = `<strong>Technical Details:</strong><br><pre>${details}</pre>`;
            errorMessage.appendChild(detailsPara);
        }
        
        errorContainer.classList.remove('d-none');
    }
    
    // Function to reset UI
    function resetUI() {
        // Reset form
        form.reset();
        
        // Reset progress bar
        progressBar.style.width = '0%';
        
        // Hide all sections except employee form
        loadingSection.classList.add('d-none');
        resultsSection.classList.add('d-none');
        errorContainer.classList.add('d-none');
        
        // Show employee form
        employeeFormSection.classList.remove('d-none');
    }
    
    // Function to simulate progress
    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            if (progress >= 90) {
                clearInterval(interval);
                return;
            }
            
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            
            progressBar.style.width = `${progress}%`;
        }, 500);
    }
    
    // Helper function to format date
    function formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}); 