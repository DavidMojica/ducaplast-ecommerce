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
                    if (action == "1"){
                        //Toast añadido
                        console.log("Producto añadido");
                    } else if (action == "2"){
                        if(window.location.href === '/cart/'){
                            if(data.carrito_vacio) window.location.href === '/cart/';
                            else{
                                $('#p-' + producto_id).remove();
                                $('#total_productos').text(`$${data.total_productos}`);
                                $('#iva').text(`$${data.iva}`);
                                $('#total_venta').text(`$${data.total_actualizado}`);
                                $('#productos_cantidad').text(`Carro - ${data.productos_cantidad} item(s)`)
                            }
                        }
                        console.log(window.location.href)
                    }
                } else {
                    alert('Error en el carrito');
                }
            },
            error: function() {
                alert('Error al procesar la solicitud');
            }
        });
    });
});