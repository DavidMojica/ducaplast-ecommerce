//-------------DOM--------------//
const formRegistro = document.getElementById('formRegistro');
const camposFormulario = document.querySelectorAll('#formRegistro input');
const spanEvento = document.getElementById('spanEvento');

console.log("salchicha")
formRegistro.addEventListener('submit', (e)=>{
    e.preventDefault();
    alert('hola')
    if (!validarFormulario()){
        spanEvento.innerText = "Algún campo está vacío";
        return;
    }
    else formRegistro.submit();
});

const validarFormulario = () => {
    camposFormulario.forEach(campo => {
        if (campo.value.trim() === '') return false;
    })
    return true;
}