const selectClient = document.getElementById('selectClient');
const createClient = document.getElementById('createClient');

const openCreateClient = document.getElementById('openCreateClient');
const openSelectClient = document.getElementById('openSelectClient');

const total_productos = document.getElementById('total_productos');
const iva = document.getElementById('iva');
let totalVenta = document.getElementById('total_venta');

let totalProductos = 0;

//Mostrar detalles de cliente o crear cliente
const showElement = element => {
    element.classList.remove('d-none');
    element.classList.add('d-block');
}

const hideElement = element => {
    element.classList.remove('d-block');
    element.classList.add('d-none');
}

openCreateClient.addEventListener('click', (e) => {
    hideElement(selectClient);
    showElement(createClient);
});

openSelectClient.addEventListener('click', (e) => {
    showElement(selectClient);
    hideElement(createClient);
});

//Actualizar el precio de cada producto
document.querySelectorAll('.product_quantity').forEach(input => {
    const priceElement = input.parentElement.nextElementSibling.querySelector('span');
    const price = (parseFloat(priceElement.textContent.replace('$', '').replace('.', '')))/input.value;
    totalProductos += price*input.value;
    const stepDown = input.parentElement.querySelector('button:first-child');
    const stepUp = input.parentElement.querySelector('button:last-child');

    input.addEventListener('input', function() {
        updateProductPrice(priceElement, price, parseInt(this.value));
    });

    stepDown.addEventListener('click', e =>{
        input.stepDown();
        updateProductPrice(priceElement, price, parseInt(input.value));
    });
    stepUp.addEventListener('click', e =>{
        input.stepUp();
        updateProductPrice(priceElement, price, parseInt(input.value));
    });
});

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

const updateProductPrice = (element, price, quantity) => {
    if (!isNaN(quantity) && quantity > 0){
        const object_price = price*quantity;
        element.textContent = addDecimal(object_price);
        updateGlobalPrice();
    } else {
        productPriceElement.textContent = "Cantidad no válida, el producto se borrará si se confirma la venta.";
    }
}

const addDecimal = n => {
    const p = Math.trunc(n).toString().split(',');
    p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return p.join('.');
}
