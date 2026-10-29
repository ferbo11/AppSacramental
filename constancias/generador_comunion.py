import io
import os

from datetime import date, datetime

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pypdf import PdfReader, PdfWriter

from constancias.utilidades import numero_o_na


# ============================================================
# CONFIGURACIÓN
# ============================================================

TAMANO_FUENTE = 14
FUENTE_NOMBRE = 'TimesNewRoman'
FUENTE_NEGRITA = 'Times-Bold'

RUTA_FUENTE = os.path.join(
    settings.BASE_DIR,
    'constancias',
    'fuentes',
    'times.ttf'
)


# ============================================================
# REGISTRAR TIMES NEW ROMAN
# ============================================================

if not os.path.exists(RUTA_FUENTE):
    raise FileNotFoundError(
        'No se encontró Times New Roman en:\n'
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

    especiales = {
        21: 'veintiuno',
        22: 'veintidós',
        23: 'veintitrés',
        24: 'veinticuatro',
        25: 'veinticinco',
        26: 'veintiséis',
        27: 'veintisiete',
        28: 'veintiocho',
        29: 'veintinueve',
    }

    if numero in especiales:
        return especiales[numero]

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

        return f'{decenas[base]} y {unidades[resto]}'

    if numero == 100:
        return 'cien'

    if numero < 200:
        return f'ciento {numero_a_letras(numero - 100)}'

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

        return f'{centenas[base]} {numero_a_letras(resto)}'

    if numero < 2000:
        return f'mil {numero_a_letras(numero - 1000)}'

    if numero < 10000:

        miles = numero // 1000
        resto = numero % 1000

        if miles == 1:
            texto = 'mil'
        else:
            texto = f'{numero_a_letras(miles)} mil'

        if resto:
            texto += f' {numero_a_letras(resto)}'

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

    if len(partes) >= 4:
        nombres = ' '.join(partes[:2])
        apellidos = ' '.join(partes[2:])
        return nombres, apellidos

    nombres = partes[0]
    apellidos = ' '.join(partes[1:])

    return nombres, apellidos


# ============================================================
# OBTENER FECHA DE PRIMERA COMUNIÓN
# ============================================================

def obtener_fecha_comunion(comunion):
    """
    Obtiene la fecha de Primera Comunión desde el registro.
    """

    posibles_campos = (
        'fecha_comunion',
        'fecha_primera_comunion',
        'fecha_sacramento',
        'fecha',
    )

    valor_fecha = None

    for campo in posibles_campos:
        valor = getattr(comunion, campo, None)

        if valor is not None and valor != '':
            valor_fecha = valor
            break

    if not valor_fecha:
        return 'No registrada'

    if isinstance(valor_fecha, datetime):
        fecha = valor_fecha.date()

    elif isinstance(valor_fecha, date):
        fecha = valor_fecha

    else:
        fecha = None
        valor_texto = str(valor_fecha).strip()

        formatos = (
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d %H:%M:%S',
        )

        for formato in formatos:
            try:
                fecha = datetime.strptime(
                    valor_texto,
                    formato
                ).date()
                break
            except ValueError:
                continue

        if fecha is None:
            return valor_texto

    return (
        f'{fecha.day} de '
        f'{MESES[fecha.month - 1]} de '
        f'{fecha.year}'
    )


# ============================================================
# DIBUJAR TEXTO CON ESTILOS
# ============================================================

def dibujar_texto_con_estilos(
    pdf,
    segmentos,
    x,
    y,
    tamano=TAMANO_FUENTE
):
    posicion_x = x

    for texto, negrita in segmentos:

        fuente = FUENTE_NEGRITA if negrita else FUENTE_NOMBRE

        pdf.setFont(
            fuente,
            tamano
        )

        pdf.drawString(
            posicion_x,
            y,
            texto
        )

        ancho = pdfmetrics.stringWidth(
            texto,
            fuente,
            tamano
        )

        posicion_x += ancho


# ============================================================
# DIBUJAR VALORES SUBRAYADOS
# ============================================================

def dibujar_valor_subrayado(
    pdf,
    texto,
    x,
    y,
    negrita=False,
    mayusculas=False
):

    if texto is None:
        return

    texto = str(texto).strip()

    if not texto:
        return

    if mayusculas:
        texto = texto.upper()

    fuente = FUENTE_NEGRITA if negrita else FUENTE_NOMBRE

    pdf.setFont(
        fuente,
        TAMANO_FUENTE
    )

    pdf.drawString(
        x,
        y,
        texto
    )

    ancho_texto = pdfmetrics.stringWidth(
        texto,
        fuente,
        TAMANO_FUENTE
    )

    pdf.setLineWidth(0.5)

    pdf.line(
        x,
        y - 2,
        x + ancho_texto,
        y - 2
    )


# ============================================================
# GENERAR CONSTANCIA DE PRIMERA COMUNIÓN
# ============================================================

def generar_constancia_comunion(
    comunion,
    numero_partida,
    observacion=''
):

    # ========================================================
    # PLANTILLA
    # ========================================================

    ruta_plantilla = os.path.join(
        settings.BASE_DIR,
        'constancias',
        'plantillas',
        'Plantilla_Primera_Comunion.pdf'
    )

    if not os.path.exists(ruta_plantilla):
        raise FileNotFoundError(
            'No se encontró la plantilla de Primera Comunión:\n'
            f'{ruta_plantilla}'
        )

    # ========================================================
    # DATOS DEL REGISTRO
    # ========================================================

    nombre, apellidos = separar_nombre(
        comunion.nombre or ''
    )

    padre = (
        comunion.nombre_padre.strip()
        if comunion.nombre_padre
        else 'No registrado'
    )

    madre = (
        comunion.nombre_madre.strip()
        if comunion.nombre_madre
        else 'No registrada'
    )

    fecha_comunion = obtener_fecha_comunion(comunion)

    if not observacion:
        observacion = 'NINGUNO'

    # ========================================================
    # CREAR CAPA TRANSPARENTE
    # ========================================================

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=(612, 792)
    )

    pdf.setFont(
        FUENTE_NOMBRE,
        TAMANO_FUENTE
    )

    # ========================================================
    # PÁRRAFO SUPERIOR
    # ========================================================

        # ========================================================
    # PÁRRAFO SUPERIOR
    # ========================================================

    libro_val = numero_o_na(
        getattr(comunion, 'libro', None),
        defecto='N/A'
    )

    folio_val = numero_o_na(
        getattr(comunion, 'folio', None),
        defecto='N/A'
    )

    partida_val = numero_o_na(
        numero_partida,
        defecto='N/A'
    )

    try:
        libro_str = (
            f'{int(libro_val):02d}'
            if str(libro_val).isdigit()
            else str(libro_val)
        )
    except (ValueError, TypeError):
        libro_str = str(libro_val)

    try:
        folio_str = (
            f'{int(folio_val):03d}'
            if str(folio_val).isdigit()
            else str(folio_val)
        )
    except (ValueError, TypeError):
        folio_str = str(folio_val)

    try:
        partida_str = (
            f'{int(partida_val):03d}'
            if str(partida_val).isdigit()
            else str(partida_val)
        )
    except (ValueError, TypeError):
        partida_str = str(partida_val)

    # ========================================================
    # TEXTO DEL REGISTRO
    # ========================================================

    texto_registro_1 = [
        ('Que ha tenido a la vista el libro del ', False),
        ('Sacramento de la Primera Comunión No. ', False),
        (libro_str, True),
        (', folio ', False),
        (folio_str, True),
        (', ', False),
    ]

    texto_registro_2 = [
        ('partida No. ', False),
        (partida_str, True),
        (', en la cual se encuentra el registro de:', False),
    ]

    dibujar_texto_con_estilos(
        pdf,
        texto_registro_1,
        x=44,
        y=520
    )

    dibujar_texto_con_estilos(
        pdf,
        texto_registro_2,
        x=44,
        y=500
    )

    # ========================================================
    # NOMBRE
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        nombre,
        237,
        460,
        negrita=True,
        mayusculas=True
    )

    # ========================================================
    # APELLIDOS
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        apellidos,
        237,
        437,
        negrita=True,
        mayusculas=True
    )

    # ========================================================
    # PADRE
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        padre,
        237,
        413
    )

    # ========================================================
    # MADRE
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        madre,
        237,
        389
    )

    # ========================================================
    # FECHA DE PRIMERA COMUNIÓN
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        fecha_comunion,
        274,
        364
    )

    # ========================================================
    # FECHA DE EXPEDICIÓN
    # ========================================================

    fecha_actual = datetime.now()

    dia = str(fecha_actual.day)
    mes = MESES[fecha_actual.month - 1]
    anio = numero_a_letras(fecha_actual.year)

    pdf.setFont(
        FUENTE_NOMBRE,
        TAMANO_FUENTE
    )

    pdf.drawString(
        44,
        315,
        'Para el uso que al interesado (a), convenga se extiende en una hoja bond'
    )

    segmentos_fecha = [
        ('membretada tamaño carta a los ', False),
        (dia, True),
        (' días del mes de ', False),
        (mes, True),
        (' del año ', False),
        (anio, True),
    ]

    dibujar_texto_con_estilos(
        pdf,
        segmentos_fecha,
        x=44,
        y=295
    )

    pdf.setFont(
        FUENTE_NOMBRE,
        TAMANO_FUENTE
    )

    pdf.drawString(
        44,
        275,
        'en la ciudad de Cobán Alta Verapaz.'
    )

    # ========================================================
    # OBSERVACIONES
    # ========================================================

    dibujar_valor_subrayado(
        pdf,
        observacion,
        132,
        215
    )

    # ========================================================
    # FINALIZAR CAPA
    # ========================================================

    pdf.save()

    buffer.seek(0)

    # ========================================================
    # COMBINAR CON PLANTILLA
    # ========================================================

    plantilla_reader = PdfReader(
        ruta_plantilla
    )

    overlay_reader = PdfReader(
        buffer
    )

    pagina_plantilla = plantilla_reader.pages[0]
    pagina_overlay = overlay_reader.pages[0]

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
