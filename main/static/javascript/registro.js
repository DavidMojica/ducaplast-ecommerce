//-------------DOM--------------//
const camposFormulario = document.querySelectorAll('#formRegistro input');
const formRegistro = document.getElementById('formRegistro');
const spanEvento = document.getElementById('spanEvento');

// Input elements
const nombre = document.getElementById('nombre');
const apellido = document.getElementById('apellidos');
const documento = document.getElementById('documento');
const password = document.getElementById('password');
const copyUsername = document.getElementById('copyUsername');
const tipoUsuario = document.getElementById('tipoUsuario');
const email = document.getElementById('email');

//Input badges
const selectSpan = tipoUsuario.parentElement.querySelector('.badge');
const spanCopy = copyUsername.parentElement.querySelector('.badge');

//Variables
const nombreMinLength = 2;
const apellidosMinLength = 3;
const documentoMinLength = 6;
const passwordMinLegth = 8;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

let validationState = undefined;

// ----------Functions---------- //
const changeBadgeColor = (type, badge) => {
    if (type == 0) {
        badge.classList.remove('bg-danger');
        badge.classList.add('bg-success');
    } else if(type == 1) {
        badge.classList.remove('bg-success');
        badge.classList.add('bg-danger');
    }
}

//Evento de escucha para submit
formRegistro.addEventListener('submit', (e)=>{
    e.preventDefault();
    validationState = validarFormulario();
    if (validationState !== '0'){
        spanEvento.innerText = validationState;
        return;
    }
    else formRegistro.submit();
});

//Valida que el formulario no tenga campos vacios y menores a 4 letras
const validarFormulario = () => {
    if (nombre.value.trim().length < nombreMinLength) return "Nombre demasiado corto.";
    if (apellido.value.trim().length < apellidosMinLength) return "Apellidos demasiado cortos";
    if (documento.value.trim().length < documentoMinLength) return "Documento demasiado corto";
    if (password.value.length < passwordMinLegth) return "Contraseña demasiado corta";
    if (tipoUsuario.value == '') return "Seleccione el tipo de usuario";
    if (!emailRegex.test(email.value.trim())) return "Ingrese un correo electrónico válido.";

    return '0';
}

//Cuando el ingrese el minimo de carácteres o más, el respectivo badge
//del campo cambiará a color verde.

nombre.addEventListener('input', (e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= nombreMinLength) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

apellido.addEventListener('input', (e)=> {
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= apellidosMinLength) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

documento.addEventListener('input', (e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= documentoMinLength) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

password.addEventListener('input', (e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.length >= passwordMinLegth) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

copyUsername.addEventListener('change', (e) => {
    const spanBadge = e.target.parentElement.querySelector('.badge');

    if (e.target.checked) {
        changeBadgeColor(0, spanBadge);
        password.value = documento.value;
    } else changeBadgeColor(1, spanBadge);
});

tipoUsuario.addEventListener('change', (e) => {
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (tipoUsuario.value !== '') changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

email.addEventListener('input', (e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if(emailRegex.test(email.value)) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});