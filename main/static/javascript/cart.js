const selectClient = document.getElementById('selectClient');
const createClient = document.getElementById('createClient');

const openCreateClient = document.getElementById('openCreateClient');
const openSelectClient = document.getElementById('openSelectClient');

function showElement(element) {
    element.classList.remove('d-none');
    element.classList.add('d-block');
}

function hideElement(element) {
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
