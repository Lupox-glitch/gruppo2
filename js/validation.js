/**
 * Client-Side Form Validation
 * CV Management System
 */

// Validation patterns
const patterns = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^[\d\s\-\+\(\)]{8,20}$/,
    url: /^https?:\/\/.+/,
    alphaNumeric: /^[a-zA-Z0-9\sàèéìòùÀÈÉÌÒÙ\-']+$/,
    password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/
};

// Validation messages
const messages = {
    required: 'Questo campo è obbligatorio',
    email: 'Inserisci un indirizzo email valido',
    phone: 'Inserisci un numero di telefono valido',
    url: 'Inserisci un URL valido (deve iniziare con http:// o https://)',
    password: 'La password deve contenere almeno 8 caratteri, una maiuscola, una minuscola e un numero',
    passwordMatch: 'Le password non corrispondono',
    minLength: (min) => `Deve contenere almeno ${min} caratteri`,
    maxLength: (max) => `Deve contenere al massimo ${max} caratteri`,
    date: 'Inserisci una data valida',
    dateRange: 'La data di fine deve essere successiva alla data di inizio',
    fileType: 'Tipo di file non valido. Solo PDF consentiti',
    fileSize: 'Il file è troppo grande. Dimensione massima: 5MB'
};

/**
 * Validate a single field
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    const fieldType = field.type;
    let error = null;

    // Clear previous error
    clearFieldError(field);

    // Required check
    if (field.hasAttribute('required') && !value) {
        error = messages.required;
    }
    // Email validation
    else if (fieldType === 'email' && value && !patterns.email.test(value)) {
        error = messages.email;
    }
    // Phone validation
    else if (field.classList.contains('phone') && value && !patterns.phone.test(value)) {
        error = messages.phone;
    }
    // URL validation
    else if (field.classList.contains('url') && value && !patterns.url.test(value)) {
        error = messages.url;
    }
    // Password strength validation
    else if (fieldType === 'password' && field.classList.contains('password-strength') && value && !patterns.password.test(value)) {
        error = messages.password;
    }
    // Min length
    else if (field.hasAttribute('minlength')) {
        const min = parseInt(field.getAttribute('minlength'));
        if (value.length > 0 && value.length < min) {
            error = messages.minLength(min);
        }
    }
    // Max length
    else if (field.hasAttribute('maxlength')) {
        const max = parseInt(field.getAttribute('maxlength'));
        if (value.length > max) {
            error = messages.maxLength(max);
        }
    }
    // Date validation
    else if (fieldType === 'date' && value) {
        const date = new Date(value);
        if (isNaN(date.getTime())) {
            error = messages.date;
        }
    }

    // Password confirmation
    if (field.classList.contains('password-confirm')) {
        const passwordField = document.querySelector('input[type="password"]:not(.password-confirm)');
        if (passwordField && value !== passwordField.value) {
            error = messages.passwordMatch;
        }
    }

    // File validation
    if (fieldType === 'file' && field.files.length > 0) {
        const file = field.files[0];
        
        // Check file type (PDF only)
        if (field.accept === '.pdf' || field.accept === 'application/pdf') {
            if (file.type !== 'application/pdf') {
                error = messages.fileType;
            }
        }
        
        // Check file size (5MB max)
        const maxSize = 5 * 1024 * 1024; // 5MB in bytes
        if (file.size > maxSize) {
            error = messages.fileSize;
        }
    }

    if (error) {
        showFieldError(field, error);
        return false;
    } else {
        showFieldSuccess(field);
        return true;
    }
}

/**
 * Show error message for a field
 */
function showFieldError(field, message) {
    field.classList.add('error');
    field.classList.remove('success');
    
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        let errorEl = formGroup.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('span');
            errorEl.className = 'form-error';
            field.parentNode.insertBefore(errorEl, field.nextSibling);
        }
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

/**
 * Show success state for a field
 */
function showFieldSuccess(field) {
    if (field.value.trim()) {
        field.classList.add('success');
        field.classList.remove('error');
    }
}

/**
 * Clear error message for a field
 */
function clearFieldError(field) {
    field.classList.remove('error', 'success');
    
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        const errorEl = formGroup.querySelector('.form-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input, textarea, select');
    let isValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Date range validation for experience forms
    const startDate = form.querySelector('input[name="data_inizio"]');
    const endDate = form.querySelector('input[name="data_fine"]');
    const isCurrent = form.querySelector('input[name="is_current"]');
    
    if (startDate && endDate && !isCurrent?.checked) {
        if (startDate.value && endDate.value) {
            if (new Date(endDate.value) < new Date(startDate.value)) {
                showFieldError(endDate, messages.dateRange);
                isValid = false;
            }
        }
    }

    return isValid;
}

/**
 * Initialize validation on form
 */
function initFormValidation(form) {
    const fields = form.querySelectorAll('input, textarea, select');

    // Validate on blur
    fields.forEach(field => {
        field.addEventListener('blur', () => {
            validateField(field);
        });

        // Real-time validation for certain fields
        if (field.type === 'email' || field.type === 'password' || field.classList.contains('url')) {
            field.addEventListener('input', debounce(() => {
                validateField(field);
            }, 500));
        }
    });

    // Validate on submit
    form.addEventListener('submit', (e) => {
        if (!validateForm(form)) {
            e.preventDefault();
            
            // Focus first error field
            const firstError = form.querySelector('.error');
            if (firstError) {
                firstError.focus();
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Show error message
            showFormMessage(form, 'Correggi gli errori nel modulo prima di inviare', 'error');
        }
    });

    // Handle "is_current" checkbox for experience forms
    const isCurrentCheckbox = form.querySelector('input[name="is_current"]');
    const endDateField = form.querySelector('input[name="data_fine"]');
    
    if (isCurrentCheckbox && endDateField) {
        isCurrentCheckbox.addEventListener('change', () => {
            if (isCurrentCheckbox.checked) {
                endDateField.disabled = true;
                endDateField.value = '';
                endDateField.required = false;
                clearFieldError(endDateField);
            } else {
                endDateField.disabled = false;
                endDateField.required = true;
            }
        });
    }
}

/**
 * Show form-level message
 */
function showFormMessage(form, message, type = 'error') {
    const alertClass = type === 'error' ? 'alert-error' : 'alert-success';
    
    // Remove existing alerts
    const existingAlert = form.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.innerHTML = `<strong>${type === 'error' ? '⚠️ Errore:' : '✓ Successo:'}</strong> ${message}`;
    
    form.insertBefore(alert, form.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Debounce helper function
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
 * File input handler with preview
 */
function initFileInput(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        const fileNameEl = document.querySelector(`#${inputId} + .file-name`);
        
        if (file) {
            if (fileNameEl) {
                fileNameEl.textContent = `Selezionato: ${file.name} (${formatFileSize(file.size)})`;
            }
            validateField(input);
        } else {
            if (fileNameEl) {
                fileNameEl.textContent = 'Nessun file selezionato';
            }
        }
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Sanitize input (prevent XSS on client side)
 */
function sanitizeInput(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Initialize all forms on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all forms with validation
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        initFormValidation(form);
    });

    // Initialize file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        if (input.id) {
            initFileInput(input.id);
        }
    });

    // Add confirm dialog for dangerous actions
    const dangerButtons = document.querySelectorAll('[data-confirm]');
    dangerButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const message = button.getAttribute('data-confirm') || 'Sei sicuro di voler continuare?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// Export functions for use in other scripts
window.CVValidation = {
    validateField,
    validateForm,
    showFormMessage,
    sanitizeInput,
    initFormValidation
};
