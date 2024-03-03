const buttons = document.querySelectorAll('.cart-handler[data-action="1"]');

        buttons.forEach(function(button) {
            const originalText = button.textContent.trim();

            button.addEventListener('click', function() {
                const badge = button.previousElementSibling;
                const deleteButton = button.parentElement.querySelector('.cart-handler[data-action="2"]');

                if (originalText === 'Agregar al carrito') {
                    button.textContent = 'Actualizar cantidad';
                    badge.textContent = 'Producto ya añadido';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-warning');
                    deleteButton.style.display = 'block';
                }
            });
        });