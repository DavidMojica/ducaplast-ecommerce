const btnModificarCantidad = document.getElementById('btnModificarCantidad');
let productosActualizados = {};
const repartidor = document.getElementById('repartidor');
const repartidorSecundario = document.getElementById('repartidorSecundario');
const consecutivo = document.getElementById('consecutivo');


const validarDespachadorForm = form => {
    if (repartidor.value != ''){
        if (repartidor.value === repartidorSecundario.value) 
            createToastNotify(1, "Error", "No puede seleccionar al mismo repartidor en ambos campos.");
        else if (consecutivo.value.trim() == 0)
            createToastNotify(1, "Error", "El campo de consecutivo no puede estar vacío");
        else form.submit();
    } else {
        if (consecutivo.value.trim() == 0)
            createToastNotify(1, "Error", "El campo de consecutivo no puede estar vacío");
        else form.submit();
    }
}

try{
    const modificarRepartidor = document.getElementById('modificarRepartidor');
    modificarRepartidor.addEventListener('submit', e => {
        e.preventDefault();
        validarDespachadorForm(modificarRepartidor);
    });
} catch {}

try {
    const confirmarRepartidor = document.getElementById('confirmarRepartidor');
    confirmarRepartidor.addEventListener('submit', e=>{
        e.preventDefault();
        validarDespachadorForm(confirmarRepartidor);
    });
} catch {}
// Tachar productos
try{
    const productos_listados = document.querySelectorAll('.producto_listado');
    productos_listados.forEach(producto =>{
        producto.addEventListener('click', ()=>{
            const strikeable_fields = producto.querySelectorAll('.strikeable_field');
            if (strikeable_fields) {
                let ban_strike = true;
                strikeable_fields.forEach(field =>{
                    if (field.value.trim().length > 0) { ban_strike = false; }
                })
                if (ban_strike){
                    const nombre_producto = producto.querySelector('.nombre_producto');
                    nombre_producto.style.textDecoration = nombre_producto.style.textDecoration === 'line-through' ? 'none' : 'line-through';
                }
            } else {
                const nombre_producto = producto.querySelector('.nombre_producto');
                nombre_producto.style.textDecoration = nombre_producto.style.textDecoration === 'line-through' ? 'none' : 'line-through';
            }
            
        });
    });
} catch {}

try{
    const strikeable_fields = document.querySelectorAll('.strikeable_field');
    strikeable_fields.forEach(field =>{
        field.addEventListener('input', e=>{
            const row = field.closest('tr');
            if (row){
                const nombre_producto = row.querySelector('.nombre_producto');
                if (nombre_producto) nombre_producto.style.textDecoration = field.value.trim().length > 0 ? 'line-through' : 'none';
            }
        });
    });
} catch {}

// Formulario de empaque
try{
    const empaqueForm = document.getElementById('empaqueForm');
    empaqueForm.addEventListener('submit', e=>{
        e.preventDefault();
        /* Estructura visionada:
        {
            id_producto: 2,
            paquete: '++',
            peso: '35 neto'
        }
        
        */
    });
} catch {}


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
                    createToastNotify(0,"Hecho","Cantidad modificada correctamente")
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

function setAction(action) {
    if (action === 'confirmarDespacho') {
        document.getElementById('confirmarRepartidorInput').disabled = false;
        document.getElementById('marcarPendienteInput').disabled = true;
    } else if (action === 'pendiente') {
        document.getElementById('confirmarRepartidorInput').disabled = true;
        document.getElementById('marcarPendienteInput').disabled = false;
    }
}
