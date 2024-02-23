//-------------DOM--------------//
const formRegistro = document.getElementById('formRegistro');
const camposFormulario = document.querySelectorAll('#formRegistro input');
const spanEvento = document.getElementById('spanEvento');

formRegistro.addEventListener('submit', (e)=>{
    e.preventDefault();
    if (!validarFormulario()){
        spanEvento.innerText = "Algún campo está vacío";
        return;
    }
    else formRegistro.submit();
});

const validarFormulario = () => {
    for (let campo of camposFormulario) {
        if (campo.value.trim() === '') {
            return false;
        }
    }
    return true;
}