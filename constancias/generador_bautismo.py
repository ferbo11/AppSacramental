
import io
import os
from datetime import date, datetime

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pypdf import PdfReader, PdfWriter

from constancias.utilidades import (
    formatear_fecha_larga,
    numero_o_defecto,
    numero_o_na,
    obtener_dato,
    obtener_fecha_local,
    texto_o_defecto,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = settings.BASE_DIR

RUTA_PLANTILLA = os.path.join(
    BASE_DIR,
    "constancias",
    "plantillas",
    "Plantilla_Bautismo.pdf",
)

RUTA_FUENTE = os.path.join(
    BASE_DIR,
    "constancias",
    "fuentes",
    "times.ttf",
)

FUENTE_NOMBRE = "TimesNewRoman"
TAMANO_FUENTE = 14


# ============================================================
# REGISTRAR FUENTE
# ============================================================

if not os.path.isfile(RUTA_FUENTE):
    raise FileNotFoundError(
        f"No se encontró la fuente: {RUTA_FUENTE}"
    )

if FUENTE_NOMBRE not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(
        TTFont(FUENTE_NOMBRE, RUTA_FUENTE)
    )


# ============================================================
# OBTENER CAMPOS
# ============================================================

def obtener_campo(objeto, nombres, defecto=""):
    """
    Obtiene el primer valor disponible de un objeto o diccionario.
    """

    for nombre in nombres:
        valor = obtener_dato(objeto, (nombre,))

        if valor is not None and str(valor).strip():
            return valor

    return defecto


# ============================================================
# FORMATEAR FECHAS
# ============================================================

def convertir_fecha(valor):
    """
    Convierte una fecha válida a datetime.date.
    Devuelve None cuando el dato no está disponible.
    """

    if not valor:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    if isinstance(valor, str):
        valor = valor.strip()

        for formato in (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ):
            try:
                return datetime.strptime(
                    valor,
                    formato,
                ).date()
            except ValueError:
                continue

    return None


def formatear_fecha_bautismo(valor):
    """
    Formatea una fecha en español sin inventar valores.
    """

    fecha = convertir_fecha(valor)

    if fecha is None:
        return ""

    meses = (
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    )

    return (
        f"{fecha.day:02d} de "
        f"{meses[fecha.month - 1]} de "
        f"{fecha.year}"
    )


# ============================================================
# DIBUJAR TEXTO CON AJUSTE DE LÍNEA
# ============================================================

def dibujar_texto_ajustado(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano=11,
    interlineado=14,
    max_lineas=2,
):
    """
    Dibuja texto dentro de un ancho máximo.
    """

    if texto is None:
        return

    texto = str(texto).strip()

    if not texto:
        return

    pdf.setFont(
        FUENTE_NOMBRE,
        tamano,
    )

    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        candidata = (
            f"{linea_actual} {palabra}".strip()
        )

        ancho_texto = pdfmetrics.stringWidth(
            candidata,
            FUENTE_NOMBRE,
            tamano,
        )

        if ancho_texto <= ancho:
            linea_actual = candidata
        else:
            if linea_actual:
                lineas.append(linea_actual)

            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    lineas = lineas[:max_lineas]

    for indice, linea in enumerate(lineas):
        pdf.drawString(
            x,
            y - indice * interlineado,
            linea,
        )


# ============================================================
# GENERAR CONSTANCIA DE BAUTISMO
# ============================================================

def generar_constancia_bautismo(
    datos,
    observacion="",
    fecha_emision=None,
):
    """
    Genera la constancia de Bautismo sobre la plantilla institucional.

    Utiliza los datos existentes del registro y no modifica
    la base de datos.
    """

    # --------------------------------------------------------
    # 1. VALIDAR PLANTILLA
    # --------------------------------------------------------

    if not os.path.isfile(RUTA_PLANTILLA):
        raise FileNotFoundError(
            "No se encontró la plantilla de Bautismo:\n"
            f"{RUTA_PLANTILLA}"
        )

    plantilla_reader = PdfReader(RUTA_PLANTILLA)

    if not plantilla_reader.pages:
        raise ValueError(
            "La plantilla de Bautismo no contiene páginas."
        )

    pagina_plantilla = plantilla_reader.pages[0]

    ancho_pagina = float(
        pagina_plantilla.mediabox.width
    )

    alto_pagina = float(
        pagina_plantilla.mediabox.height
    )

    # --------------------------------------------------------
    # 2. NOMBRE COMPLETO
    # --------------------------------------------------------

    nombre_completo = obtener_campo(
        datos,
        (
            "nombre_sacramentado",
        ),
    )
    if not nombre_completo:
        nombre_completo = obtener_campo(
            datos,
            (
                "nombre",
                "nombre_bautizado",
                "nombre_completo",
            ),
        )

    # --------------------------------------------------------
    # 3. DATOS PERSONALES
    # --------------------------------------------------------

    fecha_nacimiento = obtener_campo(
        datos,
        (
            "fecha_nacimiento",
            "fecha_de_nacimiento",
        ),
    )

    lugar_nacimiento = obtener_campo(
        datos,
        ("lugar_nacimiento",),
    )

    departamento = obtener_campo(
        datos,
        ("departamento",),
    )

    padre = obtener_campo(
        datos,
        ("padre",),
    )
    if not padre:
        padre = obtener_campo(datos, ("nombre_padre",))

    madre = obtener_campo(
        datos,
        ("madre",),
    )
    if not madre:
        madre = obtener_campo(datos, ("nombre_madre",))

    padrino_1 = obtener_campo(
        datos,
        ("padrino_1",),
    )

    padrino_2 = obtener_campo(
        datos,
        ("padrino_2",),
    )

    padrinos = " y ".join(
        str(nombre).strip()
        for nombre in (padrino_1, padrino_2)
        if nombre and str(nombre).strip()
    )

    lugar_completo = ", ".join(
        str(parte).strip()
        for parte in (
            lugar_nacimiento,
            departamento,
        )
        if parte and str(parte).strip()
    )

    # --------------------------------------------------------
    # 4. DATOS SACRAMENTALES
    # --------------------------------------------------------

    libro = numero_o_defecto(
        obtener_dato(
            datos,
            ("libro",),
        )
    )

    folio = numero_o_defecto(
        obtener_dato(
            datos,
            ("folio",),
        )
    )

    partida_valor = obtener_dato(
        datos,
        (
            "numero_partida",
            "partida",
            "partida_sacramental",
            "num_partida",
        ),
    )
    # Only use partida if there's a real source from views/models; table bautizos has no partida
    partida = numero_o_na(partida_valor, defecto="N/A")

    fecha_bautismo_original = obtener_dato(
        datos,
        (
            "fecha_bautismo",
            "fecha_sacramento",
        ),
    )

    fecha_nacimiento_texto = formatear_fecha_bautismo(
        fecha_nacimiento
    )

    fecha_bautismo_texto = formatear_fecha_bautismo(
        fecha_bautismo_original
    )

    # --------------------------------------------------------
    # 5. FECHA DE EXPEDICIÓN Y OBSERVACIONES
    # --------------------------------------------------------

    fecha_local = obtener_fecha_local(
        fecha_emision
    )

    fecha_expedicion = formatear_fecha_larga(
        fecha_local
    )

    observacion = texto_o_defecto(
        observacion,
        "NINGUNA",
    )

    # --------------------------------------------------------
    # 6. CREAR CAPA TRANSPARENTE
    # --------------------------------------------------------

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=(
            ancho_pagina,
            alto_pagina,
        ),
    )

    pdf.setTitle("Certificado de Bautizo")

    pdf.setFont(
        FUENTE_NOMBRE,
        TAMANO_FUENTE,
    )

    # --------------------------------------------------------
    # 7. TEXTO DEL REGISTRO
    # --------------------------------------------------------

    texto_registro = (
        "Que en el libro de Sacramentos de Bautismos "
        f"No. {libro}, folio {folio}, partida No. {partida}, "
        "en la cual se encuentra el registro del Bautismo de:"
    )

    dibujar_texto_ajustado(
        pdf,
        texto_registro,
        x=62,
        y=555,
        ancho=475,
        tamano=11,
        interlineado=15,
        max_lineas=3,
    )

    # --------------------------------------------------------
    # 8. VALORES ALINEADOS CON LAS ETIQUETAS
    # --------------------------------------------------------

    # Las etiquetas ya están impresas en la plantilla.
    # Se dibujan solamente los valores.
    #
    # Las coordenadas Y deben corresponder a las líneas
    # de la plantilla PDF original.

    campos = [
        # Nombre del bautizado
        (nombre_completo, 241, 496),

        # Apellidos: el nombre no se divide artificialmente
        ("", 241, 472),

        # Fecha de nacimiento
        (fecha_nacimiento_texto, 241, 448),

        # Lugar de nacimiento
        (lugar_completo, 241, 424),

        # Nombre del padre
        (padre, 241, 400),

        # Nombre de la madre
        (madre, 241, 376),

        # Padrinos
        (padrinos, 241, 352),

        # Fecha del bautizo
        (fecha_bautismo_texto, 241, 328),
    ]

    for valor, x, y in campos:
        if valor:
            dibujar_texto_ajustado(
                pdf,
                valor,
                x=x,
                y=y,
                ancho=235,
                tamano=11,
                interlineado=14,
                max_lineas=2,
            )

    # --------------------------------------------------------
    # 9. TEXTO DE EXPEDICIÓN
    # --------------------------------------------------------

    texto_expedicion = (
        "Para el uso que al interesado(a) convenga, "
        "se extiende en una hoja de papel bond "
        "membretada tamaño carta "
        f"{fecha_expedicion}, en la ciudad de "
        "Cobán, Alta Verapaz."
    )

    dibujar_texto_ajustado(
        pdf,
        texto_expedicion,
        x=90,
        y=280,
        ancho=450,
        tamano=11,
        interlineado=15,
        max_lineas=4,
    )

    # --------------------------------------------------------
    # 10. OBSERVACIONES
    # --------------------------------------------------------

    dibujar_texto_ajustado(
        pdf,
        observacion,
        x=172,
        y=191,
        ancho=350,
        tamano=11,
        interlineado=14,
        max_lineas=2,
    )

    # --------------------------------------------------------
    # 11. FINALIZAR CAPA
    # --------------------------------------------------------

    pdf.save()
    buffer.seek(0)

    overlay_reader = PdfReader(buffer)
    pagina_overlay = overlay_reader.pages[0]

    # --------------------------------------------------------
    # 12. COMBINAR CON LA PLANTILLA
    # --------------------------------------------------------

    pagina_plantilla.merge_page(
        pagina_overlay
    )

    writer = PdfWriter()
    writer.add_page(pagina_plantilla)

    resultado = io.BytesIO()

    writer.write(resultado)
    resultado.seek(0)

    buffer.close()

    return resultado
