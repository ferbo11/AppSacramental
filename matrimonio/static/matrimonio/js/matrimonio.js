function limpiarMatrimonio() {
    // Limpiar búsqueda
    document.getElementById('esposo').value = '';
    document.getElementById('esposa').value = '';

    // Limpiar resultado completo
    const resultado = document.getElementById('resultado-matrimonio');

    if (resultado) {
        resultado.innerHTML = `
            <div class="empty-result">
                <i class="fas fa-search"></i>
                <p>
                    Realice una búsqueda para consultar
                    el registro del matrimonio.
                </p>
            </div>
        `;
    }
}
