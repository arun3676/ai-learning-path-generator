/**
 * Main JavaScript file for the AI Learning Path Generator
 * Handles client-side interactivity for the web interface
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling for path generator
    const pathForm = document.getElementById('pathGeneratorForm');
    if (pathForm) {
        setupPathGenerator(pathForm);
    }
    
    // Question handling for result page
    const askButton = document.getElementById('askButton');
    if (askButton) {
        setupQuestionAsking(askButton);
    }
    
    // Initialize tooltips and other UI elements
    initUI();
});

/**
 * Set up path generator form submission
 * @param {HTMLElement} form - The form element
 */
function setupPathGenerator(form) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        
        // Gather form data
        const formData = new FormData(form);
        formData.append('type', 'human');
        
        // Convert FormData to plain object for logging
        const formDataObj = {};
        formData.forEach((value, key) => {
            formDataObj[key] = value;
        });
        console.log('Submitting form data:', formDataObj);
        
        // Submit form data via fetch API
        fetch('/generate', {
            method: 'POST',
            body: formData,  // Let the browser set the correct Content-Type with boundary
            // Don't set Content-Type header when sending FormData, let the browser handle it
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            
            if (data.success) {
                // Redirect to result page if successful
                window.location.href = data.redirect;
            } else {
                // Show error message
                showAlert('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            // Hide loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            console.error('Error:', error);
            showAlert('An error occurred. Please try again.', 'error');
        });
    });
}

/**
 * Set up question asking functionality
 * @param {HTMLElement} button - The ask button element
 */
function setupQuestionAsking(button) {
    const questionInput = document.getElementById('questionInput');
    const questionSpinner = document.getElementById('questionSpinner');
    const answerContainer = document.getElementById('answerContainer');
    const answerText = document.getElementById('answerText');
    
    button.addEventListener('click', function() {
        const question = questionInput.value.trim();
        
        if (!question) {
            showAlert('Please enter a question', 'warning');
            return;
        }
        
        // Show loading spinner
        if (questionSpinner) {
            questionSpinner.style.display = 'block';
        }
        
        // Get path information from the page
        const pathId = document.querySelector('[data-path-id]')?.dataset.pathId;
        const topic = document.querySelector('[data-path-topic]')?.dataset.pathTopic;
        
        // Prepare request data
        const requestData = {
            type: "human",
            question: question,
            path_id: pathId,
            topic: topic
        };
        
        // Submit question via fetch API
        fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            if (questionSpinner) {
                questionSpinner.style.display = 'none';
            }
            
            if (data.success !== false) {
                // Show answer container
                if (answerContainer) {
                    answerContainer.classList.remove('hidden');
                }
                if (answerText) {
                    answerText.textContent = data.answer;
                }
            } else {
                // Show error message
                showAlert('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            // Hide loading spinner
            if (questionSpinner) {
                questionSpinner.style.display = 'none';
            }
            console.error('Error:', error);
            showAlert('An error occurred. Please try again.', 'error');
        });
    });
}

/**
 * Initialize UI components
 */
function initUI() {
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add fade-in animations for elements
    const fadeElems = document.querySelectorAll('.fade-in');
    fadeElems.forEach((elem, index) => {
        setTimeout(() => {
            elem.style.opacity = '1';
            elem.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - The type of alert (success, error, warning, info)
 */
function showAlert(message, type = 'info') {
    // Check if an alert container exists, otherwise create one
    let alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alertContainer';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '1rem';
        alertContainer.style.right = '1rem';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    // Create the alert element
    const alert = document.createElement('div');
    alert.className = 'alert-message fade-in';
    alert.style.padding = '0.75rem 1rem';
    alert.style.marginBottom = '0.5rem';
    alert.style.borderRadius = '0.375rem';
    alert.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(10px)';
    alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    
    // Set styles based on type
    switch (type) {
        case 'success':
            alert.style.backgroundColor = '#d1fae5';
            alert.style.color = '#065f46';
            break;
        case 'error':
            alert.style.backgroundColor = '#fee2e2';
            alert.style.color = '#991b1b';
            break;
        case 'warning':
            alert.style.backgroundColor = '#fef3c7';
            alert.style.color = '#92400e';
            break;
        default: // info
            alert.style.backgroundColor = '#e0f2fe';
            alert.style.color = '#0369a1';
    }
    
    // Set the message
    alert.textContent = message;
    
    // Add a close button
    const closeButton = document.createElement('span');
    closeButton.innerHTML = '&times;';
    closeButton.style.float = 'right';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontWeight = 'bold';
    closeButton.style.marginLeft = '1rem';
    closeButton.addEventListener('click', () => {
        alert.remove();
    });
    
    alert.prepend(closeButton);
    
    // Add the alert to the container
    alertContainer.appendChild(alert);
    
    // Trigger animation
    setTimeout(() => {
        alert.style.opacity = '1';
        alert.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
}
