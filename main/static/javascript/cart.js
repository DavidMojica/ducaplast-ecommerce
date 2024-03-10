const selectClient = document.getElementById('selectClient');
const createClient = document.getElementById('createClient');
const openCreateClient = document.getElementById('openCreateClient');
const openSelectClient = document.getElementById('openSelectClient');
const total_productos = document.getElementById('total_productos');
const iva = document.getElementById('iva');
let totalVenta = document.getElementById('total_venta');
const form_venta = document.getElementById('form_venta');
const form_registrar_cliente =  document.getElementById('form_registrar_cliente');
const reg_cliente_direccion = document.getElementById('reg_cliente_direccion');
const reg_cliente_nombre = document.getElementById('reg_cliente_nombre');
const reg_cliente_event = document.getElementById('reg_cliente_event');
const confirmar_venta = document.getElementById('confirmar_venta');
const vender = document.getElementById('vender');

let totalProductos = 0;
const nota = document.getElementById('nota');
const Productos = {};
const cliente = document.getElementById('cliente');

confirmar_venta.addEventListener('submit', e=>{
    val_venta();
    e.preventDefault();
    if (val_venta){
        confirmar_venta.appendChild(cliente);
        confirmar_venta.appendChild(Productos);
        confirmar_venta.submit();
    }
});

const val_venta = () =>{
    console.log(cliente.value)
    console.log(Productos);
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

form_registrar_cliente.addEventListener('submit', e =>{
    e.preventDefault();
    const val = val_cliente_registro();
    if (val !== "0") createToastNotify(0, "Error al registrar", val);
    else form_registrar_cliente.submit();
    
});

const val_cliente_registro = () =>{
    if (reg_cliente_nombre.textContent.trim().length < 4 || reg_cliente_direccion.textContent.trim().length < 4) return "Nombre o dirección demasiado corta.";
    return "0";
}

const updateGlobalPrice = () => {
    totalProductos = 0;
    document.querySelectorAll('.product_quantity').forEach(input => {
        const priceElement = input.parentElement.nextElementSibling.querySelector('span');
        const price = (parseFloat(priceElement.textContent.replace('$', '').replace('.', '')))/input.value;
        totalProductos += price*input.value;
    })
    total_productos.textContent = addDecimal(totalProductos);
    iva.textContent = addDecimal(totalProductos*0.19);
    totalVenta.textContent = addDecimal(totalProductos + totalProductos*0.19);

}

const updateProductPrice = (element, price, quantity, id) => {
    if (!isNaN(quantity) && quantity > 0){
        const object_price = price*quantity;
        element.textContent = addDecimal(object_price);
        Productos[id] = quantity;
        console.log(Productos);
        updateGlobalPrice();
    } else {
        element.textContent = "Cantidad no válida, el producto se borrará si se confirma la venta.";
        delete Productos[id];
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
    const price = (parseFloat(priceElement.textContent.replace('$', '').replace('.', '')))/input.value;
    const id = input.closest('article').querySelector('.code').textContent;
    totalProductos += price*input.value;
    const stepDown = input.parentElement.querySelector('button:first-child');
    const stepUp = input.parentElement.querySelector('button:last-child');
    Productos[id] = parseInt(input.value);
    console.log(Productos);

    input.addEventListener('input', function() {
        updateProductPrice(priceElement, price, parseInt(this.value), id);
    });

    stepDown.addEventListener('click', e =>{
        input.stepDown();
        updateProductPrice(priceElement, price, parseInt(input.value), id);
    });
    stepUp.addEventListener('click', e =>{
        input.stepUp();
        updateProductPrice(priceElement, price, parseInt(input.value), id);
    });
});

