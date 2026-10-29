document.addEventListener('DOMContentLoaded', function () {
    // Buscar usuarios por nombre o rol
    const buscador = document.getElementById('buscarUsuario');

    buscador?.addEventListener('input', function () {
        const consulta = this.value.toLocaleLowerCase('es');

        document.querySelectorAll('#tablaUsuarios tbody tr').forEach(function (fila) {
            fila.hidden = !fila.innerText.toLocaleLowerCase('es').includes(consulta);
        });
    });

    // Validar que las contraseñas coincidan antes de enviar los formularios
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const password = form.querySelector('[name="password"]');
            const confirm = form.querySelector('[name="confirm_password"]');
            const nueva = form.querySelector('[name="nueva_password"]');
            const confirmarNueva = form.querySelector('[name="confirmar_nueva_password"]');

            if (password && confirm && password.value !== confirm.value) {
                event.preventDefault();
                alert('Las contraseñas no coinciden.');
                return;
            }

            if (nueva && confirmarNueva && nueva.value !== confirmarNueva.value) {
                event.preventDefault();
                alert('Las contraseñas nuevas no coinciden.');
            }
        });
    });
});

// Mostrar el panel para cambiar la contraseña de un usuario
function abrirCambioPassword(id, username) {
    const idUsuario = document.getElementById('idUsuarioPassword');
    const nombreUsuario = document.getElementById('nombreUsuarioPassword');
    const panel = document.getElementById('panelCambiarPassword');

    if (!idUsuario || !nombreUsuario || !panel) {
        return;
    }

    idUsuario.value = id;
    nombreUsuario.textContent = username;
    panel.hidden = false;
    panel.scrollIntoView({ behavior: 'smooth' });
}

// Cerrar el panel y limpiar el formulario
function cerrarCambioPassword() {
    const panel = document.getElementById('panelCambiarPassword');
    const formulario = document.getElementById('formCambiarPassword');

    if (panel) {
        panel.hidden = true;
    }

    formulario?.reset();
}