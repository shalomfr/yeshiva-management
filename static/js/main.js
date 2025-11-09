// Main JavaScript for Yeshiva Management System
// קובץ JavaScript ראשי - מערכת ניהול ישיבה

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
};

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Press Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// Utility functions
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatHebrewDate(hebrewDateString) {
    // hebrewDateString format: "1 שבט תשפ"ה"
    return hebrewDateString;
}

// Show notification
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Can be extended to show toast notifications
}

// Show error
function showError(message) {
    showNotification(message, 'error');
}

// Show success
function showSuccess(message) {
    showNotification(message, 'success');
}

// API calls wrapper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        showError(error.message);
        throw error;
    }
}

// Confirm dialog helper
function confirmAction(message) {
    return confirm(message);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded');

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('href') === currentPath ||
            (currentPath === '/' && item.getAttribute('href') === '/dashboard')) {
            item.classList.add('active');
        }
    });
});

// Export functions for use in templates
window.apiCall = apiCall;
window.showError = showError;
window.showSuccess = showSuccess;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
