// Main JavaScript file for Server Maintenance Scheduler

$(document).ready(function() {
    // Initialize the application
    initializeApp();
    
    // Update current time every second
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Handle navigation active states
    setActiveNavigation();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Server Maintenance Scheduler initialized');
    
    // Set up global error handlers
    setupErrorHandlers();
    
    // Set up AJAX defaults
    setupAjaxDefaults();
    
    // Initialize tooltips
    initializeTooltips();
}

/**
 * Update current time in the navbar
 */
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    
    $('#current-time').text(timeString);
}

/**
 * Set active navigation item based on current page
 */
function setActiveNavigation() {
    const currentPath = window.location.pathname;
    
    // Remove active class from all nav links
    $('.navbar-nav .nav-link').removeClass('active');
    
    // Add active class to current page
    $('.navbar-nav .nav-link').each(function() {
        const href = $(this).attr('href');
        if (href && currentPath.includes(href) && href !== '/') {
            $(this).addClass('active');
        } else if (currentPath === '/' && href === '/') {
            $(this).addClass('active');
        }
    });
}

/**
 * Set up global error handlers
 */
function setupErrorHandlers() {
    // Global AJAX error handler
    $(document).ajaxError(function(event, xhr, settings, thrownError) {
        console.error('AJAX Error:', {
            url: settings.url,
            status: xhr.status,
            error: thrownError
        });
        
        if (xhr.status === 0) {
            showNotification('Network connection error. Please check your internet connection.', 'error');
        } else if (xhr.status >= 500) {
            showNotification('Server error occurred. Please try again later.', 'error');
        }
    });
    
    // Global unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('An unexpected error occurred.', 'error');
    });
}

/**
 * Set up AJAX defaults
 */
function setupAjaxDefaults() {
    // Set default timeout
    $.ajaxSetup({
        timeout: 30000, // 30 seconds
        cache: false
    });
    
    // Add loading indicator for AJAX requests
    $(document).ajaxStart(function() {
        $('body').addClass('loading');
    }).ajaxStop(function() {
        $('body').removeClass('loading');
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Show notification to user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = getAlertClass(type);
    const iconClass = getIconClass(type);
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show notification-alert" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // Auto-dismiss after duration
    setTimeout(function() {
        $('.notification-alert').alert('close');
    }, duration);
}

/**
 * Get Bootstrap alert class for notification type
 * @param {string} type - The notification type
 * @returns {string} - The Bootstrap alert class
 */
function getAlertClass(type) {
    switch(type) {
        case 'success': return 'alert-success';
        case 'error': return 'alert-danger';
        case 'warning': return 'alert-warning';
        case 'info': return 'alert-info';
        default: return 'alert-info';
    }
}

/**
 * Get icon class for notification type
 * @param {string} type - The notification type
 * @returns {string} - The Font Awesome icon class
 */
function getIconClass(type) {
    switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-triangle';
        case 'warning': return 'fas fa-exclamation-circle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

/**
 * Format date for display
 * @param {string|Date} date - The date to format
 * @param {boolean} includeTime - Whether to include time (default: true)
 * @returns {string} - Formatted date string
 */
function formatDate(date, includeTime = true) {
    const dateObj = new Date(date);
    
    if (includeTime) {
        return dateObj.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } else {
        return dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

/**
 * Get relative time string (e.g., "2 hours ago", "in 3 days")
 * @param {string|Date} date - The date to compare
 * @returns {string} - Relative time string
 */
function getRelativeTime(date) {
    const now = new Date();
    const dateObj = new Date(date);
    const diffMs = dateObj.getTime() - now.getTime();
    const diffMinutes = Math.round(diffMs / (1000 * 60));
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
    
    if (Math.abs(diffMinutes) < 1) {
        return 'just now';
    } else if (Math.abs(diffMinutes) < 60) {
        return diffMinutes > 0 ? `in ${diffMinutes} minutes` : `${Math.abs(diffMinutes)} minutes ago`;
    } else if (Math.abs(diffHours) < 24) {
        return diffHours > 0 ? `in ${diffHours} hours` : `${Math.abs(diffHours)} hours ago`;
    } else {
        return diffDays > 0 ? `in ${diffDays} days` : `${Math.abs(diffDays)} days ago`;
    }
}

/**
 * Validate form data
 * @param {jQuery} form - The form element
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form) {
    let isValid = true;
    
    // Clear previous validation states
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Check required fields
    form.find('[required]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        
        if (!value) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">This field is required.</div>');
            isValid = false;
        }
    });
    
    // Check email fields
    form.find('input[type="email"]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        
        if (value && !isValidEmail(value)) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">Please enter a valid email address.</div>');
            isValid = false;
        }
    });
    
    // Check IP address fields
    form.find('input[pattern*="[0-9]"]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        const pattern = field.attr('pattern');
        
        if (value && pattern && !new RegExp(pattern).test(value)) {
            field.addClass('is-invalid');
            field.after('<div class="invalid-feedback">Please enter a valid format.</div>');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validate email address
 * @param {string} email - The email to validate
 * @returns {boolean} - Whether the email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Debounce function to limit function calls
 * @param {Function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @returns {Function} - The debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Confirm action with user
 * @param {string} message - The confirmation message
 * @param {Function} onConfirm - Callback for confirmation
 * @param {Function} onCancel - Callback for cancellation (optional)
 */
function confirmAction(message, onConfirm, onCancel = null) {
    if (confirm(message)) {
        onConfirm();
    } else if (onCancel) {
        onCancel();
    }
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @returns {Promise} - Promise that resolves when text is copied
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Generate a unique ID
 * @returns {string} - A unique identifier
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Global utility functions for server status
window.ServerUtils = {
    getStatusClass: function(status) {
        switch(status) {
            case 'online': return 'bg-success';
            case 'maintenance': return 'bg-warning text-dark';
            case 'offline': return 'bg-danger';
            default: return 'bg-secondary';
        }
    },
    
    getStatusIcon: function(status) {
        switch(status) {
            case 'online': return 'fas fa-check-circle';
            case 'maintenance': return 'fas fa-tools';
            case 'offline': return 'fas fa-times-circle';
            default: return 'fas fa-question-circle';
        }
    },
    
    getMaintenanceStatusClass: function(status) {
        switch(status) {
            case 'scheduled': return 'bg-info';
            case 'in_progress': return 'bg-warning text-dark';
            case 'completed': return 'bg-success';
            case 'cancelled': return 'bg-secondary';
            default: return 'bg-secondary';
        }
    },
    
    getMaintenanceStatusIcon: function(status) {
        switch(status) {
            case 'scheduled': return 'fas fa-calendar';
            case 'in_progress': return 'fas fa-cog fa-spin';
            case 'completed': return 'fas fa-check';
            case 'cancelled': return 'fas fa-times';
            default: return 'fas fa-question';
        }
    }
};

// Export functions for use in other scripts
window.MaintenanceApp = {
    showNotification,
    formatDate,
    getRelativeTime,
    validateForm,
    confirmAction,
    copyToClipboard,
    generateId,
    escapeHtml,
    debounce
}; 