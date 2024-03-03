$(document).ready(function() {
    $('.cart-handler').on('click', function(e) {
        e.preventDefault();
        let producto_id = $(this).data('producto-id');
        let cantidad = $(this).siblings('.cantidad').val();
        let url = $(this).data('carthandler-url');
        let action = $(this).data('action');
        let csfrtoken = $('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'action': action,
                'producto_id': producto_id,
                'cantidad': cantidad,
                'csrfmiddlewaretoken': csfrtoken
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