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
const nombreMinLength = 2;
const apellidosMinLength = 3;
const passwordMinLegth = 8;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

accountForm.addEventListener('submit', (e)=>{
    e.preventDefault();

    validationResult = accountValidations();
    if (validationResult === "0") e.submit();
    else account_event.innerText = validationResult;
});


const accountValidations = () => {
    if (nombre.value.trim().length < nombreMinLength) return "Nombre demasiado corto.";
    if (apellido.value.trim().length < apellidosMinLength) return "Apellidos demasiado cortos";
    if (!emailRegex.test(email.value.trim())) return "Ingrese un correo electrónico válido.";
    return '0';
}

passForm.addEventListener('submit', (e)=>{
    e.preventDefault();

    validationResult = passValidations();
    if(validationResult === "0") e.submit();
    else pass_event.innerText = validationResult();
})

const passValidations = () =>{
    if (password.value.trim().length < passwordMinLegth) return "Contraseña demasiado corta";
}