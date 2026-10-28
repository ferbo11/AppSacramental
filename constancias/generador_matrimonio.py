import os

from django.conf import settings

from constancias.pdf_utilidades import (
    crear_capa,
    cerrar_capa,
    combinar_con_plantilla,
    dibujar_bloque_ajustado,
    dibujar_multilinea_limitada,
    dibujar_rectangulo_blanco,
)
from constancias.utilidades import (
    formatear_fecha_larga,
    numero_o_defecto,
    numero_o_na,
    obtener_dato,
    obtener_fecha_local,
    texto_o_defecto,
)


RUTA_PLANTILLA = os.path.join(
    settings.BASE_DIR,
    'constancias',
    'plantillas',
    'Plantilla_Matrimonio.pdf',
)

NOMBRE_PENDIENTE = '____________________'
FILIACION_PENDIENTE = '____________________'
EDAD_PENDIENTE = '____'


def generar_constancia_matrimonio(
    datos,
    observacion='',
    fecha_emision=None,
):
    esposo = texto_o_defecto(
        obtener_dato(
            datos,
            (
                'nombre_esposo',
                'esposo',
            ),
        ),
        NOMBRE_PENDIENTE,
    )

    esposa = texto_o_defecto(
        obtener_dato(
            datos,
            (
                'nombre_esposa',
                'esposa',
            ),
        ),
        NOMBRE_PENDIENTE,
    )

    libro = numero_o_na(
        obtener_dato(
            datos,
            ('libro',),
        )
    )

    folio = numero_o_na(
        obtener_dato(
            datos,
            ('folio',),
        )
    )

    anio = numero_o_na(
        obtener_dato(
            datos,
            ('anio',),
        )
    )

    edad_esposo = texto_o_defecto(
        obtener_dato(
            datos,
            ('edad_esposo',),
        ),
        EDAD_PENDIENTE,
    )

    edad_esposa = texto_o_defecto(
        obtener_dato(
            datos,
            ('edad_esposa',),
        ),
        EDAD_PENDIENTE,
    )

    padre_esposo = texto_o_defecto(
        obtener_dato(
            datos,
            ('padre_esposo',),
        ),
        FILIACION_PENDIENTE,
    )

    madre_esposo = texto_o_defecto(
        obtener_dato(
            datos,
            ('madre_esposo',),
        ),
        FILIACION_PENDIENTE,
    )

    padre_esposa = texto_o_defecto(
        obtener_dato(
            datos,
            ('padre_esposa',),
        ),
        FILIACION_PENDIENTE,
    )

    madre_esposa = texto_o_defecto(
        obtener_dato(
            datos,
            ('madre_esposa',),
        ),
        FILIACION_PENDIENTE,
    )

    fecha_expedicion = formatear_fecha_larga(
        obtener_fecha_local(fecha_emision)
    )

    observacion = texto_o_defecto(
        observacion,
        'NINGUNA',
    )

    parrafos = [
        (
            'Datos del registro: Libro de Matrimonios '
            f'No. {libro}, folio {folio}, año {anio}.'
        ),
        (
            f'El MATRIMONIO DE: {esposo}, de '
            f'{edad_esposo} años de edad, hijo de '
            f'{padre_esposo} y de {madre_esposo}.'
        ),
        (
            f'Con la señorita: {esposa}, de '
            f'{edad_esposa} años de edad, hija de '
            f'{padre_esposa} y de {madre_esposa}.'
        ),
        (
            'Para el uso que al interesado(a) convenga, '
            'se extiende en una hoja bond membretada '
            'tamaño carta, '
            f'{fecha_expedicion}, en la ciudad de '
            'Cobán, Alta Verapaz.'
        ),
    ]

    buffer, pdf = crear_capa()

    pdf.setTitle(
        'Constancia de Matrimonio'
    )

    dibujar_rectangulo_blanco(
        pdf,
        30,
        285,
        552,
        185,
    )

    dibujar_bloque_ajustado(
        pdf,
        parrafos,
        72,
        540,
        270,
        468,
        tamano_max=13.0,
        tamano_min=9.0,
    )

    dibujar_multilinea_limitada(
        pdf,
        observacion,
        150,
        244,
        380,
        tamano=11.0,
        interlineado=14.0,
        max_lineas=2,
    )

    cerrar_capa(pdf, buffer)

    return combinar_con_plantilla(
        RUTA_PLANTILLA,
        buffer,
    )
