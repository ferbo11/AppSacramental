import io
import os

from django.conf import settings

from pypdf import PdfReader, PdfWriter

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ANCHO_CARTA = 612
ALTO_CARTA = 792

FUENTE_NOMBRE = 'TimesNewRoman'

RUTA_FUENTE = os.path.join(
    settings.BASE_DIR,
    'constancias',
    'fuentes',
    'times.ttf',
)

if not os.path.exists(RUTA_FUENTE):
    raise FileNotFoundError(
        'No se encontró la fuente Times New Roman.\n'
        f'Coloca el archivo times.ttf en:\n'
        f'{RUTA_FUENTE}'
    )

if FUENTE_NOMBRE not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(
        TTFont(
            FUENTE_NOMBRE,
            RUTA_FUENTE,
        )
    )


def crear_capa():
    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=(ANCHO_CARTA, ALTO_CARTA),
    )

    pdf.setFont(
        FUENTE_NOMBRE,
        14,
    )

    return buffer, pdf


def cerrar_capa(pdf, buffer):
    pdf.save()
    buffer.seek(0)

    return buffer


def _dividir_palabra(palabra, ancho_max, tamano):
    partes = []
    actual = ''

    for caracter in palabra:
        candidato = f'{actual}{caracter}'

        if (
            not actual
            or pdfmetrics.stringWidth(
                candidato,
                FUENTE_NOMBRE,
                tamano,
            ) <= ancho_max
        ):
            actual = candidato
        else:
            partes.append(actual)
            actual = caracter

    if actual:
        partes.append(actual)

    return partes


def envolver_texto(texto, ancho_max, tamano):
    palabras = str(texto).split()

    if not palabras:
        return ['']

    lineas = []
    actual = ''

    for palabra in palabras:
        candidato = f'{actual} {palabra}'.strip()

        if (
            pdfmetrics.stringWidth(
                candidato,
                FUENTE_NOMBRE,
                tamano,
            ) <= ancho_max
        ):
            actual = candidato
            continue

        if actual:
            lineas.append(actual)
            actual = ''

        if (
            pdfmetrics.stringWidth(
                palabra,
                FUENTE_NOMBRE,
                tamano,
            ) <= ancho_max
        ):
            actual = palabra
            continue

        partes = _dividir_palabra(
            palabra,
            ancho_max,
            tamano,
        )

        lineas.extend(partes[:-1])
        actual = partes[-1]

    if actual:
        lineas.append(actual)

    return lineas


def _lineas_por_parrafo(parrafos, ancho, tamano):
    return [
        envolver_texto(
            parrafo,
            ancho,
            tamano,
        )
        for parrafo in parrafos
    ]


def _recortar_linea(linea, ancho_max, tamano):
    sufijo = '...'

    while (
        linea
        and pdfmetrics.stringWidth(
            f'{linea}{sufijo}',
            FUENTE_NOMBRE,
            tamano,
        ) > ancho_max
    ):
        linea = linea[:-1]

    return f'{linea}{sufijo}' if linea else sufijo


def _altura_bloques(
    bloques,
    interlineado,
    separacion,
):
    altura = 0

    for bloque in bloques:
        altura += len(bloque) * interlineado

    if bloques:
        altura += separacion * (len(bloques) - 1)

    return altura


def _dibujar_bloques(
    pdf,
    bloques,
    x,
    y,
    tamano,
    interlineado,
    separacion,
):
    pdf.setFont(
        FUENTE_NOMBRE,
        tamano,
    )

    for indice, bloque in enumerate(bloques):
        for linea in bloque:
            pdf.drawString(x, y, linea)
            y -= interlineado

        if indice < len(bloques) - 1:
            y -= separacion

    return y


def dibujar_parrafo(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano=13,
    interlineado=17,
):
    lineas = envolver_texto(
        texto,
        ancho,
        tamano,
    )

    return _dibujar_bloques(
        pdf,
        [lineas],
        x,
        y,
        tamano,
        interlineado,
        0,
    )


def dibujar_bloque_ajustado(
    pdf,
    parrafos,
    x,
    y_inicial,
    y_minimo,
    ancho,
    tamano_max=13.0,
    tamano_min=9.0,
    interlineado_ratio=1.35,
    separacion=6.0,
):
    disponible = y_inicial - y_minimo
    tamano = tamano_max

    while tamano >= tamano_min:
        interlineado = tamano * interlineado_ratio
        bloques = _lineas_por_parrafo(
            parrafos,
            ancho,
            tamano,
        )

        if (
            _altura_bloques(
                bloques,
                interlineado,
                separacion,
            ) <= disponible
        ):
            return _dibujar_bloques(
                pdf,
                bloques,
                x,
                y_inicial,
                tamano,
                interlineado,
                separacion,
            )

        tamano -= 0.5

    tamano = tamano_min
    interlineado = tamano * interlineado_ratio
    bloques = _lineas_por_parrafo(
        parrafos,
        ancho,
        tamano,
    )

    maximo_lineas = max(
        1,
        int(disponible // interlineado),
    )

    lineas = [
        linea
        for bloque in bloques
        for linea in bloque
    ]

    if len(lineas) > maximo_lineas:
        lineas = lineas[:maximo_lineas]
        lineas[-1] = _recortar_linea(
            lineas[-1],
            ancho,
            tamano,
        )

    return _dibujar_bloques(
        pdf,
        [lineas],
        x,
        y_inicial,
        tamano,
        interlineado,
        0,
    )


def dibujar_texto_ajustado(
    pdf,
    texto,
    x,
    y,
    ancho_max,
    tamano=13.0,
    tamano_min=7.0,
):
    texto = str(texto)

    tamano_actual = tamano

    while (
        tamano_actual > tamano_min
        and pdfmetrics.stringWidth(
            texto,
            FUENTE_NOMBRE,
            tamano_actual,
        ) > ancho_max
    ):
        tamano_actual -= 0.5

    if (
        pdfmetrics.stringWidth(
            texto,
            FUENTE_NOMBRE,
            tamano_actual,
        ) > ancho_max
    ):
        while (
            len(texto) > 1
            and pdfmetrics.stringWidth(
                f'{texto}...',
                FUENTE_NOMBRE,
                tamano_actual,
            ) > ancho_max
        ):
            texto = texto[:-1]

        texto = f'{texto}...'

    pdf.setFont(
        FUENTE_NOMBRE,
        tamano_actual,
    )
    pdf.drawString(x, y, texto)


def dibujar_multilinea_limitada(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano=11.0,
    interlineado=14.0,
    max_lineas=2,
):
    lineas = envolver_texto(
        texto,
        ancho,
        tamano,
    )

    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        lineas[-1] = _recortar_linea(
            lineas[-1],
            ancho,
            tamano,
        )

    return _dibujar_bloques(
        pdf,
        [lineas],
        x,
        y,
        tamano,
        interlineado,
        0,
    )


def dibujar_rectangulo_blanco(
    pdf,
    x,
    y,
    ancho,
    alto,
):
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(
        x,
        y,
        ancho,
        alto,
        stroke=0,
        fill=1,
    )
    pdf.setFillColorRGB(0, 0, 0)


def combinar_con_plantilla(
    ruta_plantilla,
    overlay,
):
    if not os.path.exists(ruta_plantilla):
        raise FileNotFoundError(
            'No se encontró la plantilla oficial:\n'
            f'{ruta_plantilla}'
        )

    plantilla_reader = PdfReader(ruta_plantilla)
    overlay_reader = PdfReader(overlay)

    pagina = plantilla_reader.pages[0]
    pagina.merge_page(
        overlay_reader.pages[0]
    )

    writer = PdfWriter()
    writer.add_page(pagina)

    resultado = io.BytesIO()
    writer.write(resultado)
    resultado.seek(0)

    return resultado
