const regexNumeros = input => {
    return /^[0-9]+$/.test(input);
}

$(document).ready(()=> {
    $('.cart-handler').on('click', function(e) {
        e.preventDefault();
        let producto_id = $(this).data('producto-id');
        let cantidad = $(this).siblings('.cantidad').val();
        let url = $(this).data('carthandler-url');
        let action = $(this).data('action');
        let csfrtoken = $('input[name="csrfmiddlewaretoken"]').val();
        //Validar desde el servidor: cantidad nula o 0, regex numero.

        if (cantidad.trim() == "" || cantidad <= 0 || !regexNumeros(cantidad)) createToastNotify(1, "Error, cantidad no válida.", "Por favor ingrese una cantidad de producto válida.");
        else{
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
                success: data => {
                    if (data.success) {
                        if (action == "1")createToastNotify(0, "Producto añadido/actualizado.", "El producto fue añadido o actualizado correctamente.");
                        else if (action == "2") createToastNotify(1, "Producto removido", "Producto removido del carrito correctamente.");
                    } else createToastNotify(1, "Error", "Opción no válida.");
                },
                error: ()=> {
                    createToastNotify(1, "Error al procesar la solicitud.", "En el proceso de verificación de datos, algo salió mal.");
                }
            });
        }
    });
});