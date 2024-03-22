const btnModificarCantidad = document.getElementById('btnModificarCantidad');
let productosActualizados = {};
let ban = true;
$(btnModificarCantidad).on('click', function(e){
    e.preventDefault();
    
    const modificarCantidad = document.querySelectorAll('.modificarCantidad');
    modificarCantidad.forEach((fila)=>{
        cantidad = fila.querySelector('input[type="number"]').value;
        productosActualizados[parseInt(fila.querySelector('input[type="hidden"]').value)] = cantidad;
        if (cantidad <= 0) ban = false;
    });

    if (ban){
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
    }
    else {
        createToastNotify(1, "Error en cantidad", "La cantidad de los productos debe de ser mayor a 0. Si no necesita los productos, borrelos.")
    }
});