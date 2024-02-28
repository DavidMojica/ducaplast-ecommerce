const accountForm = document.getElementById('accountForm');
const passForm = document.getElementById('passForm');

const nombre = document.getElementById('nombre');
const apellidos = document.getElementById('apellidos');
const email = document.getElementById('email');
const account_event = document.getElementById('account_event');

const oldPassword = document.getElementById('oldPassword');
const password = document.getElementById('password');
const password1 = document.getElementById('password1');
const pass_event = document.getElementById('pass_event');

//Variables
let validationResult = undefined;
let badgeChild = undefined;
const nombreMinLength = 2;
const apellidosMinLength = 3;
const passwordMinLegth = 8;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

//---------------Functions--------------//
const changeBadgeColor = (type, badge) => {
    if (type == 0) {
        badge.classList.remove('bg-danger');
        badge.classList.add('bg-success');
    } else if(type == 1) {
        badge.classList.remove('bg-success');
        badge.classList.add('bg-danger');
    }
}

accountForm.addEventListener('submit', function(e){
    e.preventDefault();

    validationResult = accountValidations();
    if (validationResult === "0") {
        accountForm.submit();

    }
    else account_event.innerText = validationResult;
});

function accountValidations() {
    if (nombre.value.trim().length < nombreMinLength) return "Nombre demasiado corto.";
    if (apellidos.value.trim().length < apellidosMinLength) return "Apellidos demasiado cortos";
    if (!emailRegex.test(email.value.trim())) return "Ingrese un correo electrónico válido.";
    return '0';
}


passForm.addEventListener('submit', function(e){
    e.preventDefault();

    validationResult = passValidations();
    if(validationResult === "0") {
        passForm.submit();
    }
    else pass_event.innerText = validationResult;
})

function passValidations() {
    if (oldPassword.value.length < passwordMinLegth) return "La contraseña antigua es demasiado corta";
    if (password.value.length < passwordMinLegth) return "La contraseña nueva es demasiado corta";
    if (password1.value.length < passwordMinLegth) return "Confirmar contraseña es demasiado corta";
    if (password.value !== password1.value) return "Las contraseñas no coinciden";

    return "0";
}

//------------DOM BADGE INTERACTION----------//

nombre.addEventListener('input',(e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= nombreMinLength) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

apellidos.addEventListener('input',(e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= apellidosMinLength) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

email.addEventListener('input', (e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if(emailRegex.test(email.value)) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

oldPassword.addEventListener('input',(e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= passwordMinLegth) changeBadgeColor(0, spanBadge);
    else changeBadgeColor(1, spanBadge);
});

password.addEventListener('input',(e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= passwordMinLegth && (password.value === password1.value)){
        changeBadgeColor(0, spanBadge);
        badgeChild = password1.parentElement.querySelector('.badge');
        changeBadgeColor(0,badgeChild);
    }
    else changeBadgeColor(1, spanBadge);
});

password1.addEventListener('input',(e)=>{
    const spanBadge = e.target.parentElement.querySelector('.badge');
    if (e.target.value.trim().length >= passwordMinLegth && (password.value === password1.value)){
        changeBadgeColor(0, spanBadge);
        badgeChild = password.parentElement.querySelector('.badge');
        changeBadgeColor(0,badgeChild);
    }
    else changeBadgeColor(1, spanBadge);
});

//--------Init DOM badge-------//

badgeChild = nombre.parentElement.querySelector('.badge');
if (nombre.value.trim().length >= nombreMinLength) changeBadgeColor(0, badgeChild);


badgeChild = apellidos.parentElement.querySelector('.badge');
if (apellidos.value.trim().length >= apellidosMinLength) changeBadgeColor(0, badgeChild);

badgeChild = email.parentElement.querySelector('.badge');
if (emailRegex.test(email.value)) changeBadgeColor(0, badgeChild);