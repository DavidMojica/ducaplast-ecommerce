document.addEventListener('DOMContentLoaded', ()=> {
    const addButtons = document.querySelectorAll('.add');
    const eliminateButtons = document.querySelectorAll('.eliminate');
    
    addButtons.forEach( addButton => {
        let deleteButton = addButton.parentElement.querySelector('.eliminate');
        
        addButton.addEventListener('click', ()=> {
            const badge = addButton.parentElement.querySelector('.badge'); 
            addButton.textContent = 'Actualizar cantidad';
            badge.textContent = 'Producto ya añadido';
            badge.classList.remove('bg-success');
            badge.classList.add('bg-warning');
            addButton.classList.remove('btn-success');
            addButton.classList.add('btn-warning');
            deleteButton = addButton.parentElement.querySelector('.eliminate');
            if (deleteButton) {
                deleteButton.style.display = 'inline-block';
            }
        });

    });

    eliminateButtons.forEach((eliminateButton)=> {
        eliminateButton.addEventListener('click', (e)=> {
            const addButton = eliminateButton.parentElement.querySelector('.add');
            const badge = eliminateButton.parentElement.querySelector('.badge');
            addButton.textContent = 'Agregar al carrito';
            addButton.classList.remove('btn-warning');
            addButton.classList.add('btn-success');
            badge.classList.remove('bg-warning');
            badge.classList.add('bg-success');
            badge.textContent = 'Cantidad';
            eliminateButton.style.display = 'none';
            e.stopPropagation(); // Evitar que el evento se propague a los botones de agregar
        });
    });
});
