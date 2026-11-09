import os

from django.conf import settings

from reportlab.pdfbase import pdfmetrics

from constancias.pdf_utilidades import (
    FUENTE_NOMBRE,
    crear_capa,
    cerrar_capa,
    combinar_con_plantilla,
    dibujar_bloque_ajustado,
    dibujar_multilinea_limitada,
)
from constancias.utilidades import (
    MESES,
    convertir_a_fecha,
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

DATO_PENDIENTE = 'N/A'

TAMANO_NOMBRE_CONTRAYENTE = 12.0
TAMANO_MINIMO_CONTRAYENTE = 11.0
TAMANO_EDAD = 10.5
TAMANO_FILIACION = 10.5
TAMANO_MINIMO_FILIACION = 10.5
TAMANO_BLOQUE = 10.5
TAMANO_OBSERVACION = 11.0


def _formatear_fecha_matrimonio(datos):
    """Devuelve la fecha del matrimonio lista para la constancia."""

    fecha = convertir_a_fecha(
        obtener_dato(
            datos,
            ('fecha_matrimonio', 'fecha'),
        )
    )

    if fecha is not None:
        return (
            f'el {fecha.day} de '
            f'{MESES[fecha.month - 1]} de '
            f'{fecha.year}'
        )

    mes = texto_o_defecto(
        obtener_dato(datos, ('mes',)),
        '',
    )

    dia = numero_o_defecto(
        obtener_dato(datos, ('dia',)),
        '',
    )

    anio = numero_o_defecto(
        obtener_dato(datos, ('ano', 'anio')),
        '',
    )

    if dia and mes and anio:
        return f'el {dia} de {mes.lower()} de {anio}'

    if mes and anio:
        return f'en el mes de {mes.lower()} de {anio}'

    if anio:
        return f'en el año {anio}'

    if dia and mes:
        return f'el {dia} de {mes.lower()}'

    return 'en fecha no registrada'


def _testigos(datos):
    testigos = [
        str(testigo).strip()
        for testigo in (
            obtener_dato(datos, ('testigo_1',)),
            obtener_dato(datos, ('testigo_2',)),
        )
        if testigo and str(testigo).strip()
    ]

    if not testigos:
        return 'No se registraron testigos.'

    if len(testigos) == 1:
        return f'Fue testigo: {testigos[0]}.'

    return f'Fueron testigos: {" y ".join(testigos)}.'


def _dibujar_en_hueco(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano_max=12.0,
    tamano_min=8.0,
):
    """Escribe un valor dentro del espacio libre de la plantilla."""

    texto = str(texto).strip()

    if not texto:
        return

    tamano = tamano_max

    while (
        tamano > tamano_min
        and pdfmetrics.stringWidth(
            texto,
            FUENTE_NOMBRE,
            tamano,
        ) > ancho
    ):
        tamano -= 0.25

    ancho_texto = pdfmetrics.stringWidth(
        texto,
        FUENTE_NOMBRE,
        tamano,
    )

    escala = 100.0

    if ancho_texto > ancho:
        escala = max(
            (ancho / ancho_texto) * 100.0,
            55.0,
        )

        if ancho_texto * escala / 100.0 > ancho:
            sufijo = '...'
            recortado = texto

            while (
                len(recortado) > 1
                and pdfmetrics.stringWidth(
                    f'{recortado}{sufijo}',
                    FUENTE_NOMBRE,
                    tamano,
                ) * escala / 100.0 > ancho
            ):
                recortado = recortado[:-1]

            texto = (
                f'{recortado}{sufijo}'
                if recortado
                else sufijo
            )

    texto_pdf = pdf.beginText(x, y)
    texto_pdf.setFont(FUENTE_NOMBRE, tamano)

    if escala < 100.0:
        texto_pdf.setHorizScale(escala)

    texto_pdf.textOut(texto)
    pdf.drawText(texto_pdf)


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
        DATO_PENDIENTE,
    )

    esposa = texto_o_defecto(
        obtener_dato(
            datos,
            (
                'nombre_esposa',
                'esposa',
            ),
        ),
        DATO_PENDIENTE,
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

    anio_valor = obtener_dato(
        datos,
        ('anio', 'ano'),
    )

    if anio_valor is None:
        fecha_registro = convertir_a_fecha(
            obtener_dato(
                datos,
                ('fecha_matrimonio',),
            )
        )

        if fecha_registro is not None:
            anio_valor = fecha_registro.year

    anio = numero_o_na(anio_valor)

    edad_esposo = numero_o_na(
        obtener_dato(
            datos,
            ('edad_esposo',),
        )
    )

    edad_esposa = numero_o_na(
        obtener_dato(
            datos,
            ('edad_esposa',),
        )
    )

    padre_esposo = texto_o_defecto(
        obtener_dato(
            datos,
            ('padre_esposo',),
        ),
        DATO_PENDIENTE,
    )

    madre_esposo = texto_o_defecto(
        obtener_dato(
            datos,
            ('madre_esposo',),
        ),
        DATO_PENDIENTE,
    )

    padre_esposa = texto_o_defecto(
        obtener_dato(
            datos,
            ('padre_esposa',),
        ),
        DATO_PENDIENTE,
    )

    madre_esposa = texto_o_defecto(
        obtener_dato(
            datos,
            ('madre_esposa',),
        ),
        DATO_PENDIENTE,
    )

    fecha_matrimonio = _formatear_fecha_matrimonio(datos)

    testigos = _testigos(datos)

    fecha_expedicion = formatear_fecha_larga(
        obtener_fecha_local(fecha_emision)
    )

    observacion = texto_o_defecto(
        observacion,
        'NINGUNA',
    )

    buffer, pdf = crear_capa()

    pdf.setTitle(
        'Constancia de Matrimonio'
    )

    # Datos dentro de los espacios libres de la plantilla oficial.
    _dibujar_en_hueco(
        pdf,
        esposo,
        166.5,
        445.75,
        95.0,
        tamano_max=TAMANO_NOMBRE_CONTRAYENTE,
        tamano_min=TAMANO_MINIMO_CONTRAYENTE,
    )
    _dibujar_en_hueco(
        pdf,
        edad_esposo,
        277.0,
        445.75,
        12.5,
        tamano_max=TAMANO_EDAD,
        tamano_min=TAMANO_EDAD,
    )

    _dibujar_en_hueco(
        pdf,
        padre_esposo,
        89.0,
        429.65,
        43.5,
        tamano_max=TAMANO_FILIACION,
        tamano_min=TAMANO_MINIMO_FILIACION,
    )
    _dibujar_en_hueco(
        pdf,
        madre_esposo,
        162.0,
        429.65,
        405.0,
        tamano_max=TAMANO_FILIACION,
        tamano_min=TAMANO_MINIMO_FILIACION,
    )

    _dibujar_en_hueco(
        pdf,
        esposa,
        139.5,
        397.45,
        127.0,
        tamano_max=TAMANO_NOMBRE_CONTRAYENTE,
        tamano_min=TAMANO_MINIMO_CONTRAYENTE,
    )
    _dibujar_en_hueco(
        pdf,
        edad_esposa,
        281.5,
        397.45,
        12.5,
        tamano_max=TAMANO_EDAD,
        tamano_min=TAMANO_EDAD,
    )

    _dibujar_en_hueco(
        pdf,
        padre_esposa,
        88.5,
        381.35,
        78.0,
        tamano_max=TAMANO_FILIACION,
        tamano_min=TAMANO_MINIMO_FILIACION,
    )
    _dibujar_en_hueco(
        pdf,
        madre_esposa,
        200.0,
        381.35,
        368.0,
        tamano_max=TAMANO_FILIACION,
        tamano_min=TAMANO_MINIMO_FILIACION,
    )

    # Bloque de registro, fecha, testigos y expedición.
    dibujar_bloque_ajustado(
        pdf,
        [
            (
                'Datos del registro: Libro de Matrimonios '
                f'No. {libro}, folio {folio}, año {anio}.'
            ),
            f'Contrajeron matrimonio {fecha_matrimonio}.',
            testigos,
            (
                'Para el uso que al interesado(a) convenga, '
                'se extiende en una hoja bond membretada '
                'tamaño carta, '
                f'{fecha_expedicion}, en la ciudad de '
                'Cobán, Alta Verapaz.'
            ),
        ],
        72,
        365,
        255,
        468,
        tamano_max=TAMANO_BLOQUE,
        tamano_min=TAMANO_BLOQUE,
        interlineado_ratio=1.35,
        separacion=4.0,
    )

    dibujar_multilinea_limitada(
        pdf,
        observacion,
        137.5,
        248.4,
        430,
        tamano=TAMANO_OBSERVACION,
        interlineado=14.0,
        max_lineas=2,
    )

    cerrar_capa(pdf, buffer)

    return combinar_con_plantilla(
        RUTA_PLANTILLA,
        buffer,
    )
