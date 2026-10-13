document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reservationForm");
    const calendarDays = document.getElementById("calendarDays");
    const currentMonth = document.getElementById("currentMonth");
    const prevMonth = document.getElementById("prevMonth");
    const nextMonth = document.getElementById("nextMonth");
    const appointmentsList = document.getElementById("appointmentsList");
    const fechaInput = document.getElementById("fecha");
    const message = document.getElementById("agendaMessage");
    const totalActividades = document.getElementById("totalActividades");
    const actividadesHoy = document.getElementById("actividadesHoy");
    const actividadesProximas = document.getElementById("actividadesProximas");

    if (
        !form ||
        !calendarDays ||
        !currentMonth ||
        !appointmentsList ||
        !fechaInput
    ) {
        console.error("No se encontraron los elementos de la agenda.");
        return;
    }

    let actividades = [];
    let fechaSeleccionada = "";

    const hoy = new Date();
    let mesActual = new Date(hoy.getFullYear(), hoy.getMonth(), 1);

    const meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];

    function actualizarContadores() {
    // Obtener la fecha local actual.
    const ahora = new Date();

    const hoyISO = [
        ahora.getFullYear(),
        String(ahora.getMonth() + 1).padStart(2, "0"),
        String(ahora.getDate()).padStart(2, "0")
    ].join("-");

    // Total de actividades registradas en SQLite.
    totalActividades.textContent = actividades.length;

    // Actividades programadas para hoy.
    const totalHoy = actividades.filter(
        actividad => actividad.fecha === hoyISO
    ).length;

    actividadesHoy.textContent = totalHoy;

    // Actividades programadas desde hoy en adelante.
    const totalProximas = actividades.filter(
        actividad => actividad.fecha >= hoyISO
    ).length;

    actividadesProximas.textContent = totalProximas;
}
    function fechaISO(anio, mes, dia) {
        return [
            anio,
            String(mes + 1).padStart(2, "0"),
            String(dia).padStart(2, "0")
        ].join("-");
    }

   function mostrarMensaje(texto, error = false) {
    let overlay = document.getElementById("agendaPopupOverlay");

    // Crear el popup solamente una vez.
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "agendaPopupOverlay";
        overlay.className = "agenda-popup-overlay";

        overlay.innerHTML = `
            <section
                class="agenda-popup"
                role="alertdialog"
                aria-modal="true"
                aria-labelledby="agendaPopupTitle"
                aria-describedby="agendaPopupText"
            >
                <div class="agenda-popup-icon" id="agendaPopupIcon"></div>

                <h2 class="agenda-popup-title" id="agendaPopupTitle"></h2>

                <p class="agenda-popup-text" id="agendaPopupText"></p>

                <button
                    type="button"
                    class="agenda-popup-button"
                    id="agendaPopupClose"
                >
                    Entendido
                </button>
            </section>
        `;

        document.body.appendChild(overlay);

        // Cerrar con el botón.
        overlay.querySelector("#agendaPopupClose")
            .addEventListener("click", cerrarPopup);

        // Cerrar al hacer clic fuera de la tarjeta.
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) {
                cerrarPopup();
            }
        });

        // Cerrar con Escape.
        document.addEventListener("keydown", (event) => {
            if (
                event.key === "Escape" &&
                overlay.classList.contains("is-visible")
            ) {
                cerrarPopup();
            }
        });
    }

    const popup = overlay.querySelector(".agenda-popup");
    const icono = overlay.querySelector("#agendaPopupIcon");
    const titulo = overlay.querySelector("#agendaPopupTitle");
    const mensajePopup = overlay.querySelector("#agendaPopupText");

    // Configurar el tipo de notificación.
    popup.className = `agenda-popup ${error ? "error" : "success"}`;

    icono.textContent = error ? "✕" : "✓";
    titulo.textContent = error ? "Ocurrió un problema" : "¡Excelente!";
    mensajePopup.textContent = texto;

    // Mostrar el popup.
    overlay.classList.add("is-visible");

    // Mantener accesible el mensaje existente sin mostrarlo debajo.
    if (message) {
        message.textContent = "";
    }
}

function cerrarPopup() {
    const overlay = document.getElementById("agendaPopupOverlay");

    if (overlay) {
        overlay.classList.remove("is-visible");
    }
}

    async function cargarActividades() {
        try {
            const respuesta = await fetch(
                "/agenda/actividades/",
                {
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            if (!respuesta.ok) {
                throw new Error("No se pudieron consultar las actividades.");
            }

            const datos = await respuesta.json();

            actividades = datos.actividades;
            
            actualizarContadores();
            renderizarCalendario();
            renderizarProximasActividades();

        } catch (error) {
            console.error(error);
            mostrarMensaje(
                "No se pudieron cargar las actividades.",
                true
            );
        }
    }

    function renderizarCalendario() {
        calendarDays.replaceChildren();

        const anio = mesActual.getFullYear();
        const mes = mesActual.getMonth();

        currentMonth.textContent = `${meses[mes]} ${anio}`;

        const primerDia = new Date(anio, mes, 1).getDay();
        const totalDias = new Date(anio, mes + 1, 0).getDate();

        for (let i = 0; i < primerDia; i++) {
            const espacio = document.createElement("div");
            espacio.className = "calendar-empty";
            espacio.setAttribute("aria-hidden", "true");

            calendarDays.appendChild(espacio);
        }

        for (let dia = 1; dia <= totalDias; dia++) {
            const fecha = fechaISO(anio, mes, dia);

            const eventos = actividades.filter(
                actividad => actividad.fecha === fecha
            );

            const boton = document.createElement("button");

            boton.type = "button";
            boton.className = "calendar-day";
            boton.textContent = dia;
            boton.dataset.fecha = fecha;

            if (fecha === fechaISO(
                hoy.getFullYear(),
                hoy.getMonth(),
                hoy.getDate()
            )) {
                boton.classList.add("is-today");
            }

            if (fecha === fechaSeleccionada) {
                boton.classList.add("is-selected");
            }

            if (eventos.length > 0) {
                boton.classList.add("is-reserved");
                boton.title = eventos
                    .map(evento => `${evento.hora} - ${evento.sacramento}`)
                    .join("\n");
                boton.setAttribute(
                    "aria-label",
                    `${dia}, ${eventos.length} actividad(es)`
                );
            }

            boton.addEventListener("click", () => {
                fechaSeleccionada = fecha;
                fechaInput.value = fecha;

                renderizarCalendario();
            });

            calendarDays.appendChild(boton);
        }
    }

    function renderizarProximasActividades() {
        appointmentsList.replaceChildren();

        const hoyISO = fechaISO(
            hoy.getFullYear(),
            hoy.getMonth(),
            hoy.getDate()
        );

        const proximas = actividades
            .filter(actividad => actividad.fecha >= hoyISO)
            .sort((a, b) => {
                const fechaA = `${a.fecha}T${a.hora}`;
                const fechaB = `${b.fecha}T${b.hora}`;

                return fechaA.localeCompare(fechaB);
            });

        if (proximas.length === 0) {
            const vacio = document.createElement("p");

            vacio.className = "empty-appointment";
            vacio.textContent = "No hay actividades próximas registradas.";

            appointmentsList.appendChild(vacio);
            return;
        }

        proximas.forEach(actividad => {
            const tarjeta = document.createElement("article");
            tarjeta.className = "appointment-item";

            const titulo = document.createElement("h3");
            titulo.textContent = actividad.sacramento;

            const nombre = document.createElement("p");
            nombre.textContent = actividad.nombre;

            const fecha = document.createElement("p");

            const [anio, mes, dia] = actividad.fecha
                .split("-")
                .map(Number);

            const fechaLocal = new Date(anio, mes - 1, dia);

            fecha.textContent =
                `${fechaLocal.toLocaleDateString("es-GT")} · ` +
                actividad.hora;

            tarjeta.append(titulo, nombre, fecha);

            if (actividad.observaciones) {
                const observaciones = document.createElement("p");
                observaciones.textContent = actividad.observaciones;
                tarjeta.appendChild(observaciones);
            }

            appointmentsList.appendChild(tarjeta);
        });
    }

    prevMonth?.addEventListener("click", () => {
        mesActual = new Date(
            mesActual.getFullYear(),
            mesActual.getMonth() - 1,
            1
        );

        renderizarCalendario();
    });

    nextMonth?.addEventListener("click", () => {
        mesActual = new Date(
            mesActual.getFullYear(),
            mesActual.getMonth() + 1,
            1
        );

        renderizarCalendario();
    });

    fechaInput.addEventListener("change", () => {
        if (!fechaInput.value) return;

        fechaSeleccionada = fechaInput.value;

        const [anio, mes] = fechaSeleccionada
            .split("-")
            .map(Number);

        mesActual = new Date(anio, mes - 1, 1);

        renderizarCalendario();
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!form.reportValidity()) return;

        const csrfToken = form.querySelector(
            "[name=csrfmiddlewaretoken]"
        )?.value;

        if (!csrfToken) {
            mostrarMensaje(
                "No se encontró el token de seguridad CSRF.",
                true
            );
            return;
        }

        const boton = form.querySelector("[type=submit]");

        boton.disabled = true;

        try {
            const respuesta = await fetch(
                form.action,
                {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Accept": "application/json"
                    }
                }
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error || "No se pudo registrar la actividad."
                );
            }

            mostrarMensaje(datos.mensaje);

            form.reset();

            fechaSeleccionada = "";

            await cargarActividades();

        } catch (error) {
            mostrarMensaje(error.message, true);
        } finally {
            boton.disabled = false;
        }
    });

    cargarActividades();
});