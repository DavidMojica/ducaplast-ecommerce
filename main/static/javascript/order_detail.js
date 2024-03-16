const btnModificarCantidad = document.getElementById('btnModificarCantidad');
let productosActualizados = {};

$(btnModificarCantidad).on('click', function(e){
    const modificarCantidad = document.querySelectorAll('.modificarCantidad');
    modificarCantidad.forEach((fila)=>{
        productosActualizados[fila.querySelector('input[type="hidden"]').value] = fila.querySelector('input[type="number"]').value;
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