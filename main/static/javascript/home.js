const documentoField = document.getElementById('documento');
const passwordField = document.getElementById('password');
const formInicio = document.getElementById('formInicio');
const spanEvento = document.getElementById('spanEvento');
const passhelper = document.getElementById('passhelper');

let validationState = undefined;
//Evento de escucha submit para formulario
formInicio.addEventListener('submit', (e)=>{
    e.preventDefault()

    validationState = validarFormulario();
    if (validationState != '0'){
        spanEvento.innerText = validationState;
    }
    else formInicio.submit();
});

const validarFormulario = () =>{
    if (documentoField.value.trim().length < 6) return "Documento muy corto.\nMínimo 6 carácteres";
    else if (passwordField.value.trim().length < 8) return "Contraseña muy corta\nMínimo 8 carácteres.";

    return '0';
}

passhelper.addEventListener('click', ()=>{
    spanEvento.classList.remove('bg-danger');
    spanEvento.classList.add('bg-info');
    spanEvento.textContent = "Comuniquele a un administrador para que le reinicie la contraseña. Otorguele el ID de usuario o su nombre.";
    setTimeout(() => {
        spanEvento.classList.remove('bg-info');
        spanEvento.classList.add('bg-danger');
        spanEvento.textContent = "";
    }, 10000);
});