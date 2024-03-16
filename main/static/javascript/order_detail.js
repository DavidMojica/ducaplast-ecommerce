const btnModificarCantidad = document.getElementById('btnModificarCantidad');
let productosActualizados = {};

$(btnModificarCantidad).on('click', function(e){
    e.preventDefault();
    const modificarCantidad = document.querySelectorAll('.modificarCantidad');
    modificarCantidad.forEach((fila)=>{
        productosActualizados[parseInt(fila.querySelector('input[type="hidden"]').value)] = fila.querySelector('input[type="number"]').value;
    });

    let url = $(this).attr('action');
    let csfrtoken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        type:'POST',
        url: url,
        data: {
            'action': 0,
            'csrfmiddlewaretoken': csfrtoken,
            'productos': JSON.stringify(productosActualizados),
            'modificarProductos': true,
        },
        dataType: 'json',
        success: data => {
            if (data.success){
                $('.price').text(data.total_actualizado);
            }
            else createToastNotify(1, "Error", data.msg);
        },
        error: (jqxhr, log,log2)=> {
            console.log(jqxhr)
            console.log(log);
            console.log(log2);
            createToastNotify(1, "Error al procesar la solicitud.", "En el proceso de verificación de datos, algo salió mal.");
        }
    });
});

$('.delete-item').on('click', function(e){
    e.preventDefault();
    let producto_id = $(this).data('producto-id');
    let url = $(this).attr('action');
    let csfrtoken = $('input[name="csrfmiddlewaretoken"]').val();
    console.log(producto_id)
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'producto_id':producto_id,
            'csrfmiddlewaretoken': csfrtoken,
            'borrarProducto':true
        },
        dataType: 'json',
        success: data =>{
            if (data.success) {
                const productoElement = $('#p-' + producto_id);
                productoElement.remove();
                $('.price').text(data.total_actualizado);
                $('#modalBorrarProducto-' + producto_id).modal('hide');
                $('.modal-backdrop').hide();
                
            }
        }
    })
});