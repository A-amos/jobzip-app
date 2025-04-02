document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            // Add your search logic here
        }, 300));
    }

    // Notification read status
    const notificationItems = document.querySelectorAll('.dropdown-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.add('read');
            // Add your notification read logic here
        });
    });

    // Image gallery
    const galleryImages = document.querySelectorAll('.company-image');
    galleryImages.forEach(image => {
        image.addEventListener('click', function() {
            const src = this.src;
            const modal = document.createElement('div');
            modal.classList.add('modal', 'fade');
            modal.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content bg-darker">
                        <div class="modal-body p-0">
                            <button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-3" data-bs-dismiss="modal"></button>
                            <img src="${src}" class="img-fluid" style="width: 100%;">
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            modal.addEventListener('hidden.bs.modal', function() {
                modal.remove();
            });
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // AJAX form submissions
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = this.action;
            const method = this.method;

            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Handle success
                    if (data.message) {
                        showAlert('success', data.message);
                    }
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    // Handle error
                    showAlert('danger', data.message || 'An error occurred');
                }
            })
            .catch(error => {
                showAlert('danger', 'An error occurred');
            });
        });
    });
});

// Utility functions
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'fade', 'show');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.content-area').insertAdjacentElement('afterbegin', alertDiv);
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Handle sidebar responsiveness
window.addEventListener('resize', function() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (window.innerWidth <= 768) {
        sidebar.style.width = '70px';
        mainContent.style.marginLeft = '70px';
    } else {
        sidebar.style.width = '250px';
        mainContent.style.marginLeft = '250px';
    }
});
