import io
import os

from datetime import datetime

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pypdf import PdfReader, PdfWriter


# ============================================================
# CONFIGURACIÓN
# ============================================================

TAMANO_FUENTE = 14

FUENTE_NOMBRE = 'TimesNewRoman'


# ============================================================
# FUENTE TIMES NEW ROMAN
# ============================================================

RUTA_FUENTE = os.path.join(
    settings.BASE_DIR,
    'constancias',
    'fuentes',
    'times.ttf'
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
            RUTA_FUENTE
        )
    )


# ============================================================
# MESES
# ============================================================

MESES = [
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
]


# ============================================================
# NÚMEROS A LETRAS
# ============================================================

def numero_a_letras(numero):

    unidades = [
        'cero',
        'uno',
        'dos',
        'tres',
        'cuatro',
        'cinco',
        'seis',
        'siete',
        'ocho',
        'nueve',
        'diez',
        'once',
        'doce',
        'trece',
        'catorce',
        'quince',
        'dieciséis',
        'diecisiete',
        'dieciocho',
        'diecinueve',
        'veinte',
    ]

    if 0 <= numero <= 20:
        return unidades[numero]

    if numero == 21:
        return 'veintiuno'

    if numero == 22:
        return 'veintidós'

    if numero == 23:
        return 'veintitrés'

    if numero == 24:
        return 'veinticuatro'

    if numero == 25:
        return 'veinticinco'

    if numero == 26:
        return 'veintiséis'

    if numero == 27:
        return 'veintisiete'

    if numero == 28:
        return 'veintiocho'

    if numero == 29:
        return 'veintinueve'

    if numero < 100:

        decenas = {
            30: 'treinta',
            40: 'cuarenta',
            50: 'cincuenta',
            60: 'sesenta',
            70: 'setenta',
            80: 'ochenta',
            90: 'noventa',
        }

        base = (numero // 10) * 10
        resto = numero % 10

        if resto == 0:
            return decenas[base]

        return (
            f'{decenas[base]} '
            f'y {unidades[resto]}'
        )

    if numero == 100:
        return 'cien'

    if numero < 200:

        return (
            f'ciento '
            f'{numero_a_letras(numero - 100)}'
        )

    if numero < 1000:

        centenas = {
            200: 'doscientos',
            300: 'trescientos',
            400: 'cuatrocientos',
            500: 'quinientos',
            600: 'seiscientos',
            700: 'setecientos',
            800: 'ochocientos',
            900: 'novecientos',
        }

        base = (numero // 100) * 100
        resto = numero % 100

        if resto == 0:
            return centenas[base]

        return (
            f'{centenas[base]} '
            f'{numero_a_letras(resto)}'
        )

    if numero < 2000:

        return (
            f'mil '
            f'{numero_a_letras(numero - 1000)}'
        )

    if numero < 10000:

        miles = numero // 1000
        resto = numero % 1000

        if miles == 1:
            texto = 'mil'
        else:
            texto = (
                f'{numero_a_letras(miles)} '
                f'mil'
            )

        if resto:
            texto += (
                f' {numero_a_letras(resto)}'
            )

        return texto

    return str(numero)


# ============================================================
# SEPARAR NOMBRE
# ============================================================

def separar_nombre(nombre):

    partes = nombre.strip().split()

    if not partes:
        return '', ''

    if len(partes) == 1:
        return partes[0], ''

    # En este formato usamos los dos primeros
    # elementos como nombres y el resto como apellidos.
    if len(partes) >= 4:
        nombres = ' '.join(partes[:2])
        apellidos = ' '.join(partes[2:])
        return nombres, apellidos

    # Para nombres de tres elementos:
    # dejamos el primero como nombre y los demás como apellidos.
    nombres = partes[0]
    apellidos = ' '.join(partes[1:])

    return nombres, apellidos

# ============================================================
# PADRINOS
# ============================================================

def obtener_padrinos(confirmacion):

    padrinos = []

    if confirmacion.nombre_padrino:

        padrinos.append(
            confirmacion.nombre_padrino.strip()
        )

    if confirmacion.nombre_madrina:

        padrinos.append(
            confirmacion.nombre_madrina.strip()
        )

    if not padrinos:
        return 'No registrados'

    if len(padrinos) == 1:
        return padrinos[0]

    return ' y '.join(padrinos)


# ============================================================
# TEXTO DE FECHA DE EMISIÓN
# ============================================================

def obtener_fecha_emision():

    fecha = datetime.now()

    dia = fecha.day

    mes = MESES[
        fecha.month - 1
    ]

    anio = numero_a_letras(
        fecha.year
    )

    return (
        f'a los {dia} días del mes de '
        f'{mes} del año {anio}'
    )


# ============================================================
# GENERAR CONSTANCIA DE CONFIRMACIÓN
# ============================================================

def generar_constancia_confirmacion(
    confirmacion,
    numero_partida,
    observacion=''
):

    # ========================================================
    # PLANTILLA OFICIAL
    # ========================================================

    ruta_plantilla = os.path.join(
        settings.BASE_DIR,
        'constancias',
        'plantillas',
        'Plantilla_Confirmaciones.pdf'
    )

    if not os.path.exists(ruta_plantilla):

        raise FileNotFoundError(
            'No se encontró la plantilla oficial:\n'
            f'{ruta_plantilla}'
        )

    # ========================================================
    # DATOS DEL REGISTRO
    # ========================================================

    nombre, apellidos = separar_nombre(
        confirmacion.nombre or ''
    )

    padre = (
        confirmacion.nombre_padre.strip()
        if confirmacion.nombre_padre
        else 'No registrado'
    )

    madre = (
        confirmacion.nombre_madre.strip()
        if confirmacion.nombre_madre
        else 'No registrada'
    )

    padrinos = obtener_padrinos(
        confirmacion
    )

    if confirmacion.fecha:

        fecha_confirmacion = (
            confirmacion.fecha.strftime(
                '%d/%m/%Y'
            )
        )

    else:

        fecha_confirmacion = 'No registrada'

    if not observacion:
        observacion = 'NINGUNA'

    # ========================================================
    # CREAR CAPA TRANSPARENTE
    # ========================================================

    buffer = io.BytesIO()

    # Tamaño carta
    ancho = 612
    alto = 792

    pdf = canvas.Canvas(
        buffer,
        pagesize=(ancho, alto)
    )

    pdf.setFont(
        FUENTE_NOMBRE,
        TAMANO_FUENTE
    )

    # ========================================================
    # PÁRRAFO SUPERIOR
    # ========================================================

    texto_registro_1 = (
        'Que ha tenido a la vista el libro del '
        'Sacramento de Confirmación No. '
        f'{int(confirmacion.libro):02d}, '
        'folio '
        f'{int(confirmacion.folio):03d}, '
    )

    texto_registro_2 = (
        'partida No. '
        f'{int(numero_partida):03d} '
        'en la cual se encuentra el registro de:'
    )

    pdf.drawString(
        72,
        560,
        texto_registro_1
    )

    pdf.drawString(
        72,
        540,
        texto_registro_2
    )

    # ========================================================
    # DATOS DE LA PERSONA
    # ========================================================

    pdf.drawString(
        125,
        495,
        nombre
    )

    pdf.drawString(
        130,
        471,
        apellidos
    )

    pdf.drawString(
        180,
        447,
        padre
    )

    pdf.drawString(
        195,
        422,
        madre
    )

    pdf.drawString(
        125,
        398,
        padrinos
    )

    pdf.drawString(
        207,
        374,
        fecha_confirmacion
    )

    # ========================================================
    # FECHA DE EMISIÓN
    # ========================================================
    texto_fecha_emision = obtener_fecha_emision()

    pdf.drawString(
    72,
    295,
    'Para el uso que al interesado (a), convenga se extiende en una hoja bond'
    )

    pdf.drawString(
    72,
    275,
    f'membretada tamaño carta {texto_fecha_emision}'
    )

    pdf.drawString(
    72,
    255,
    'en la ciudad de Cobán Alta Verapaz.'
    )
    
    
    # ========================================================
    # OBSERVACIONES
    # ========================================================

    pdf.drawString(
        175,
        233,
        observacion
    )

    # ========================================================
    # FINALIZAR CAPA
    # ========================================================

    pdf.save()

    buffer.seek(0)

    # ========================================================
    # COMBINAR CON PLANTILLA OFICIAL
    # ========================================================

    plantilla_reader = PdfReader(
        ruta_plantilla
    )

    overlay_reader = PdfReader(
        buffer
    )

    pagina_plantilla = (
        plantilla_reader.pages[0]
    )

    pagina_overlay = (
        overlay_reader.pages[0]
    )

    pagina_plantilla.merge_page(
        pagina_overlay
    )

    writer = PdfWriter()

    writer.add_page(
        pagina_plantilla
    )

    resultado = io.BytesIO()

    writer.write(
        resultado
    )

    resultado.seek(0)

    return resultado