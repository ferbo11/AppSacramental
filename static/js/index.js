document.addEventListener('DOMContentLoaded', function () {

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

                labels: [
                    'Bautismo',
                    'Primera Comunión',
                    'Confirmación',
                    'Matrimonio'
                ],

                datasets: [

                    {
                        label: 'Constancias emitidas',

                        data: [
                            150,
                            95,
                            80,
                            45
                        ]
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            stepSize: 25
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

                                return (
                                    context.parsed.y +
                                    ' constancias'
                                );

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

                labels: [
                    'Enero',
                    'Febrero',
                    'Marzo',
                    'Abril',
                    'Mayo',
                    'Junio',
                    'Julio',
                    'Agosto',
                    'Septiembre',
                    'Octubre',
                    'Noviembre',
                    'Diciembre'
                ],

                datasets: [

                    {
                        label: 'Constancias emitidas',

                        data: [
                            18,
                            25,
                            31,
                            22,
                            38,
                            42,
                            35,
                            47,
                            29,
                            40,
                            36,
                            44
                        ],

                        tension: 0.3,

                        fill: false
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

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

                labels: [
                    'Bautismo',
                    'Primera Comunión',
                    'Confirmación',
                    'Matrimonio'
                ],

                datasets: [

                    {
                        label: 'Constancias',

                        data: [
                            150,
                            95,
                            80,
                            45
                        ]
                    }

                ]

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

                                return (
                                    context.label +
                                    ': ' +
                                    context.parsed +
                                    ' constancias'
                                );

                            }

                        }

                    }

                }

            }

        });

    }

});