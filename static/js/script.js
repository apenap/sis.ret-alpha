// Funciones JavaScript para la aplicación

document.addEventListener('DOMContentLoaded', function() {
    // Tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Confirmación antes de eliminar
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este registro? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
    
    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Por favor, complete todos los campos obligatorios.');
            }
        });
    });
    
    // Búsqueda en tiempo real (para futuras implementaciones)
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            // Implementar búsqueda AJAX aquí
        }, 300));
    }
    
    // Función debounce para optimizar búsquedas
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
    
    // Mostrar/ocultar contraseña
    const togglePassword = document.querySelector('.toggle-password');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordInput = document.querySelector('#password');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
});

// Función para formatear precios
function formatPrice(price) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(price);
}

// Función para calcular totales
function calculateTotal() {
    const rows = document.querySelectorAll('.product-row');
    let total = 0;
    
    rows.forEach(row => {
        const price = parseFloat(row.querySelector('.price').textContent.replace(/[^\d.-]/g, ''));
        const quantity = parseInt(row.querySelector('.quantity').value) || 0;
        const rowTotal = price * quantity;
        
        row.querySelector('.row-total').textContent = formatPrice(rowTotal);
        total += rowTotal;
    });
    
    document.querySelector('#total-amount').textContent = formatPrice(total);
}

// API calls
async function searchProducts(query) {
    try {
        const response = await fetch(`/api/productos/buscar?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        return products;
    } catch (error) {
        console.error('Error buscando productos:', error);
        return [];
    }
}