//-------------DOM--------------//
const camposFormulario = document.querySelectorAll('#formRegistro input');
const formRegistro = document.getElementById('formRegistro');
const spanEvento = document.getElementById('spanEvento');
const copyUsername = document.getElementById('copyUsername');
const documento = document.getElementById('documento');
const password = document.getElementById('password');
const tipoUsuario = document.getElementById('tipoUsuario');
const selectSpan = tipoUsuario.parentElement.querySelector('.badge');
const spanCopy = copyUsername.parentElement.querySelector('.badge');

//Evento de escucha para submit
formRegistro.addEventListener('submit', (e)=>{
    e.preventDefault();
    if (!validarFormulario()){
        spanEvento.innerText = "Algún campo tiene datos muy cortos.";
        return;
    }
    else formRegistro.submit();
});

//Valida que el formulario no tenga campos vacios y menores a 4 letras
const validarFormulario = () => {
    for (let campo of camposFormulario) {
        if (campo.value.trim().length <= 4) {
            return false;
        }
    }
    return true;
}

//Cuando el usuario ingrese 4 carácteres o más, el respectivo badge
//cambiará a color verde.
formRegistro.addEventListener('input', function(event) {
    if (event.target.tagName === 'INPUT') {
        const spanBadge = event.target.parentElement.querySelector('.badge');
        if (event.target.value.trim().length >= 4) {
            spanBadge.classList.remove('bg-danger');
            spanBadge.classList.add('bg-success');
        } else {
            spanBadge.classList.remove('bg-success');
            spanBadge.classList.add('bg-danger');
        }
    }
});

tipoUsuario.addEventListener('change', () => {
    if (tipoUsuario.value !== '') {
        selectSpan.classList.remove('bg-danger');
        selectSpan.classList.add('bg-success');
    } else {
        selectSpan.classList.remove('bg-success');
        selectSpan.classList.add('bg-danger');
    }
});

//Copiar documento a password
copyUsername.addEventListener('change', (event) => {
    if (event.target.checked) {
        spanCopy.classList.remove('bg-danger');
        spanCopy.classList.add('bg-success');
        password.value = documento.value;
    } else {
        spanCopy.classList.remove('bg-success');
        spanCopy.classList.add('bg-danger');
    }
});