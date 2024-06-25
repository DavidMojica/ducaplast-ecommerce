const selectClient = document.getElementById('selectClient');
const createClient = document.getElementById('createClient');

const openCreateClient = document.getElementById('openCreateClient');
const openSelectClient = document.getElementById('openSelectClient');

const total_productos = document.getElementById('total_productos');
const iva = document.getElementById('iva');
let totalVenta = document.getElementById('total_venta');

const form_venta = document.getElementById('form_venta');

let totalProductos = 0;
const Productos = {};
const ProductosParaEliminar = {};
const nota = document.getElementById('nota');
const cliente = document.getElementById('cliente');
const urgente = document.getElementById('urgente');

var myModal = document.getElementById('myModal')
var myInput = document.getElementById('myInput')

try {
    form_registrar_cliente.addEventListener('submit', e =>{
        e.preventDefault();
        const val = val_cliente_registro();
        if (val !== "0") createToastNotify(1, "Error al registrar", val);
        else form_registrar_cliente.submit();
        
    });
} catch {}

const val_cliente_registro = () =>{
    if (reg_cliente_nombre.value.trim().length < 4 || reg_cliente_direccion.value.trim().length < 4) return "Nombre o dirección demasiado corta.";
    return "0";
}

const updateProduct = (element, id, quantity) => {
    if (!isNaN(quantity) && quantity > 0){
        Productos[id]['cantidad'] = quantity;
        element.textContent = "";
        delete ProductosParaEliminar[id];
    }else {
        element.textContent = "Cantidad no válida, el producto se borrará si se confirma la venta.";
        ProductosParaEliminar[id] = true;
    }
}

const updateQuantityType = (id, quantity_type) =>{
    if (!isNaN(quantity_type)){
        Productos[id]['tipo_cantidad'] = quantity_type;
        console.log(Productos);
    }
}

const addDecimal = n => {
    const p = Math.trunc(n).toString().split(',');
    p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return p.join('.');
}

//Mostrar detalles de cliente o crear cliente
const showElement = element => {
    element.classList.remove('d-none');
    element.classList.add('d-block');
}

const hideElement = element => {
    element.classList.remove('d-block');
    element.classList.add('d-none');
}

try{
    openCreateClient.addEventListener('click', (e) => {
        hideElement(selectClient);
        showElement(createClient);
    });
    
    openSelectClient.addEventListener('click', (e) => {
        showElement(selectClient);
        hideElement(createClient);
    });
} catch {}

//Actualizar el precio de cada producto
document.querySelectorAll('.product_quantity').forEach(input => {
    const priceElement = input.parentElement.nextElementSibling.querySelector('span');
    // const price = (parseFloat(priceElement.textContent.replace('$', '').replace('.', '')))/input.value;
    const id = input.closest('article').querySelector('.code').textContent;
    // totalProductos += price*input.value;
    const stepDown = input.parentElement.querySelector('button:first-child');
    const stepUp = input.parentElement.querySelector('button:last-child');
    const product_quantity_type = input.parentElement.nextElementSibling.nextElementSibling;
    //Init
    Productos[id] = {'cantidad': parseInt(input.value), 'tipo_cantidad': parseInt(product_quantity_type.value)};
    input.addEventListener('input', function() {
        // updateProductPrice(priceElement, price, parseInt(this.value), id);
        console.log(Productos);
        updateProduct(priceElement, id, parseInt(input.value));
        console.log(Productos);
    });

    stepDown.addEventListener('click', e =>{
        input.stepDown();
        updateProduct(priceElement, id, parseInt(input.value));
        // updateProductPrice(priceElement, price, parseInt(input.value), id);
    });

    stepUp.addEventListener('click', e =>{
        input.stepUp();
        updateProduct(priceElement, id, parseInt(input.value));
        // updateProductPrice(priceElement, price, parseInt(input.value), id);
    });
});

document.querySelectorAll('.product_quantity_type').forEach(input =>{
    const id = input.closest('article').querySelector('.code').textContent;
    input.addEventListener('change', ()=>{
        updateQuantityType(id, parseInt(input.value));
    });
});

try{
    confirmar_venta.addEventListener('submit', e=>{
        e.preventDefault();
        if (val_venta()){
            $(document).ready(()=>{
                let csfrtoken = $('input[name="csrfmiddlewaretoken"]').val();
                let url = $(this).attr('action');

                for (let id in ProductosParaEliminar){
                    if (ProductosParaEliminar[id]) delete Productos[id];
                }

                const urgente_value = urgente.checked ? true : false;

                $.ajax({
                    type: 'POST',
                    url: url,
                    data:{
                        'productos': JSON.stringify(Productos),
                        'cliente':cliente.value.trim(),
                        'nota':nota.value.trim(),
                        'urgente':urgente_value,
                        'confirmar_venta': true,
                        'csrfmiddlewaretoken': csfrtoken
                    },
                    dataType: 'json',
                    success: data =>{
                        if (data.success){
                            window.location.href = '/orders/';
                        } else createToastNotify(1, "Error", data.msg);
                    },
                    error: (jqxhr, log,log2)=> {
                        // console.log(jqxhr)
                        // console.log(log);
                        // console.log(log2);
                        createToastNotify(1, "Error al procesar la solicitud.", "En el proceso de verificación de datos, algo salió mal.");
                    }
                });
            });
        }
    });
} catch {}

const val_venta = () =>{
    if (cliente.value.trim() === "" || isNaN(cliente.value)){
        createToastNotify(1, "Error al vender", "Seleccione un cliente");
        return false;
    }
    else if (Productos.length <= 0){
        createToastNotify(1, "Error al vender", "Seleccione products");
        return false;
    }
    return true;
}

