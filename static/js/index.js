document.addEventListener('DOMContentLoaded', function () {

    /*
     * ========================================
     * DATOS PROCEDENTES DE DJANGO
     * ========================================
     */

    const obtenerDatos = (id, valorPorDefecto = []) => {
        const elemento = document.getElementById(id);

        if (!elemento) {
            console.error(`No se encontró el elemento ${id}`);
            return valorPorDefecto;
        }

        try {
            return JSON.parse(elemento.textContent);
        } catch (error) {
            console.error(`Error al leer ${id}:`, error);
            return valorPorDefecto;
        }
    };

    const etiquetasSacramentos = obtenerDatos(
        'etiquetas-sacramentos'
    );

    const datosSacramentos = obtenerDatos(
        'datos-sacramentos'
    );

    const etiquetasMeses = obtenerDatos(
        'etiquetas-meses'
    );

    const datosMeses = obtenerDatos(
        'datos-meses'
    );


    /*
     * ========================================
     * GRÁFICA 1
     * TOTAL DE CONSTANCIAS POR SACRAMENTO
     * ========================================
     */

    const constanciasCanvas =
        document.getElementById('constanciasChart');

    if (constanciasCanvas) {

        new Chart(constanciasCanvas, {

            type: 'bar',

            data: {
                labels: etiquetasSacramentos,

                datasets: [{
                    label: 'Constancias emitidas',
                    data: datosSacramentos
                }]
            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0,
                            stepSize: 1
                        },

                        title: {
                            display: true,
                            text: 'Cantidad de constancias'
                        }
                    },

                    x: {
                        title: {
                            display: true,
                            text: 'Sacramento'
                        }
                    }

                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {
                                return context.parsed.y +
                                    ' constancias';
                            }

                        }

                    }

                }

            }

        });

    }


    /*
     * ========================================
     * GRÁFICA 2
     * EMISIONES POR MES
     * ========================================
     */

    const emisionesCanvas =
        document.getElementById('emisionesMesChart');

    if (emisionesCanvas) {

        new Chart(emisionesCanvas, {

            type: 'line',

            data: {

                labels: etiquetasMeses,

                datasets: [{

                    label: 'Constancias emitidas',

                    data: datosMeses,

                    tension: 0.3,

                    fill: false

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0,
                            stepSize: 1
                        },

                        title: {
                            display: true,
                            text: 'Constancias'
                        }

                    },

                    x: {

                        title: {
                            display: true,
                            text: 'Mes'
                        }

                    }

                },

                plugins: {

                    tooltip: {

                        callbacks: {

                            label: function (context) {
                                return context.parsed.y +
                                    ' constancias';
                            }

                        }

                    }

                }

            }

        });

    }


    /*
     * ========================================
     * GRÁFICA 3
     * DISTRIBUCIÓN POR SACRAMENTO
     * ========================================
     */

    const distribucionCanvas =
        document.getElementById('distribucionChart');

    if (distribucionCanvas) {

        new Chart(distribucionCanvas, {

            type: 'doughnut',

            data: {

                labels: etiquetasSacramentos,

                datasets: [{

                    label: 'Constancias',

                    data: datosSacramentos

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        position: 'bottom'
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return context.label +
                                    ': ' +
                                    context.parsed +
                                    ' constancias';

                            }

                        }

                    }

                }

            }

        });

    }

});