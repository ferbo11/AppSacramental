function limpiarMatrimonio() {
    // Limpiar búsqueda
    const campos = ['esposo', 'esposa', 'libro', 'folio', 'ano'];

    campos.forEach(function (id) {
        const campo = document.getElementById(id);

        if (campo) {
            campo.value = '';
        }
    });

    // Limpiar resultado completo
    const resultado = document.getElementById('resultado-matrimonio');

    if (resultado) {
        resultado.innerHTML = `
            <div class="empty-result">
                <i class="fas fa-user-search"></i>
                <p>
                    Realice una búsqueda por esposo, esposa,
                    libro, folio o año para consultar el
                    registro del matrimonio.
                </p>
            </div>
        `;
    }
}


function validarConstanciaMatrimonio(formulario, requiereRevision) {
    const confirmacion = formulario.querySelector(
        'input[name="confirmar_datos"]'
    );

    if (confirmacion && !confirmacion.checked) {
        alert(
            'Debe confirmar que revisó la información del ' +
            'registro antes de emitir la constancia.'
        );
        confirmacion.focus();
        return false;
    }

    if (requiereRevision) {
        return confirm(
            'Este matrimonio está marcado para revisión. ' +
            '¿Desea generar la constancia de todos modos?'
        );
    }

    return true;
}
