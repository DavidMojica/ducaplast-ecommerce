$(document).ready(function() {
    $('.agregar-al-carrito').on('click', function(e) {
        e.preventDefault();
        let producto_id = $(this).data('producto-id');
        let cantidad = $(this).siblings('.cantidad').val();
        let url = $(this).data('carthandler-url');
        
        $.ajax({
            type: 'GET',
            url: url,
            data: {
                'producto_id': producto_id,
                'cantidad': cantidad,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    alert('Producto agregado al carrito');
                } else {
                    alert('Error al agregar el producto al carrito');
                }
            },
            error: function() {
                alert('Error al procesar la solicitud');
            }
        });
    });
});