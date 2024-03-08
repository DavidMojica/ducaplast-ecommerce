const selectClient = document.getElementById('selectClient');
const createClient = document.getElementById('createClient');

const openCreateClient = document.getElementById('openCreateClient');
const openSelectClient = document.getElementById('openSelectClient');


document.querySelectorAll('.product_quantity').forEach(input => {
    const priceElement = input.parentElement.nextElementSibling.querySelector('span');
    const price = parseFloat(priceElement.textContent.replace('$', '').replace('.', ''));

    input.addEventListener('input', function() {
        const quantity = parseInt(this.value);
        const total = quantity * price;
        priceElement.textContent = addDecimal(total);
    });

    const stepDown = input.parentElement.querySelector('button:first-child');
    const stepUp = input.parentElement.querySelector('button:last-child');

    stepDown.addEventListener('click', e =>{
        input.stepDown();
        const quantity = parseInt(input.value);
        const total = quantity * price;
        priceElement.textContent = addDecimal(total);
    });
    stepUp.addEventListener('click', e =>{
        input.stepUp();
        const quantity = parseInt(input.value);
        const total = quantity * price;
        priceElement.textContent = addDecimal(total);
    });
});


function addDecimal(number) {
    const str = number.toFixed(2);
    const parts = str.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join('.');
}









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
