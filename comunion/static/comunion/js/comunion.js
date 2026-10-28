function limpiarComunion() {
    // Limpiar búsqueda
    document.getElementById('nombre').value = '';
    document.getElementById('apellidos').value = '';

    // Limpiar resultado completo
    const resultado = document.getElementById('resultado-comunion');

    if (resultado) {
        resultado.innerHTML = `
            <div class="empty-result">
                <i class="fas fa-user-search"></i>
                <p>
                    Realice una búsqueda para consultar
                    el registro de Primera Comunión.
                </p>
            </div>
        `;
    }
}
