$(document).ready(function() {
    $('.agregar-al-carrito').on('click', function(e) {
        e.preventDefault();
        var producto_id = $(this).data('producto-id');
        var cantidad = $(this).siblings('.cantidad').val();
        console.log(`p: ${producto_id} c: ${cantidad}`)
        $.ajax({
            type: 'POST',
            url: '{% url "agregar_al_carrito" %}',
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