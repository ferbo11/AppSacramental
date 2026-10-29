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
    numero_a_letras,
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
FUENTE_NEGRITA = "Times-Bold"
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
    """Obtiene el primer valor disponible."""

    for nombre in nombres:
        valor = obtener_dato(objeto, (nombre,))

        if valor is not None and str(valor).strip():
            return valor

    return defecto


# ============================================================
# SEPARAR NOMBRE Y APELLIDOS
# ============================================================

def separar_nombre(nombre):
    """Separa nombres y apellidos siguiendo la regla existente."""

    partes = str(nombre or "").strip().split()

    if not partes:
        return "", ""

    if len(partes) == 1:
        return partes[0], ""

    if len(partes) >= 4:
        return " ".join(partes[:2]), " ".join(partes[2:])

    return partes[0], " ".join(partes[1:])


# ============================================================
# FORMATEAR FECHAS
# ============================================================

def convertir_fecha(valor):
    """Convierte una fecha válida a datetime.date."""

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
    """Devuelve la fecha en español."""

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
# DIBUJAR TEXTO AJUSTADO
# ============================================================

def dibujar_texto_ajustado(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano=TAMANO_FUENTE,
    interlineado=17,
    max_lineas=2,
):
    """Dibuja texto ajustado al ancho disponible."""

    if texto is None:
        return

    texto = str(texto).strip()

    if not texto:
        return

    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        candidata = f"{linea_actual} {palabra}".strip()

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

    pdf.setFont(FUENTE_NOMBRE, tamano)

    for indice, linea in enumerate(lineas[:max_lineas]):
        pdf.drawString(
            x,
            y - indice * interlineado,
            linea,
        )


# ============================================================
# DIBUJAR TEXTO SUBRAYADO
# ============================================================

def dibujar_texto_subrayado(
    pdf,
    texto,
    x,
    y,
    tamano=TAMANO_FUENTE,
    negrita=False,
):
    """Dibuja texto subrayado, con negrita opcional."""

    if texto is None:
        return

    texto = str(texto).strip()

    if not texto:
        return

    fuente = FUENTE_NEGRITA if negrita else FUENTE_NOMBRE

    pdf.setFont(fuente, tamano)
    pdf.drawString(x, y, texto)

    ancho_texto = pdfmetrics.stringWidth(
        texto,
        fuente,
        tamano,
    )

    pdf.setLineWidth(0.6)
    pdf.line(
        x,
        y - 2,
        x + ancho_texto,
        y - 2,
    )


def dibujar_texto_subrayado_ajustado(
    pdf,
    texto,
    x,
    y,
    ancho,
    tamano=TAMANO_FUENTE,
    interlineado=17,
    max_lineas=2,
    negrita=False,
):
    """Ajusta el texto y subraya cada línea."""

    if texto is None:
        return

    texto = str(texto).strip()

    if not texto:
        return

    fuente = FUENTE_NEGRITA if negrita else FUENTE_NOMBRE

    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        candidata = f"{linea_actual} {palabra}".strip()

        ancho_texto = pdfmetrics.stringWidth(
            candidata,
            fuente,
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

    for indice, linea in enumerate(lineas[:max_lineas]):
        dibujar_texto_subrayado(
            pdf,
            linea,
            x,
            y - indice * interlineado,
            tamano=tamano,
            negrita=negrita,
        )


# ============================================================
# DIBUJAR TEXTO CON SEGMENTOS EN NEGRITA
# ============================================================

def dibujar_texto_con_estilos(
    pdf,
    segmentos,
    x,
    y,
    ancho,
    tamano=TAMANO_FUENTE,
    interlineado=18,
    max_lineas=4,
):
    """
    Dibuja texto con segmentos en negrita.

    Cada segmento es una tupla:
        (texto, negrita)
    """

    palabras_estilizadas = []

    for texto, negrita in segmentos:
        for palabra in str(texto).split():
            palabras_estilizadas.append(
                (palabra, negrita)
            )

    lineas = []
    linea_actual = []
    ancho_actual = 0

    for palabra, negrita in palabras_estilizadas:
        fuente = (
            FUENTE_NEGRITA
            if negrita
            else FUENTE_NOMBRE
        )

        ancho_palabra = pdfmetrics.stringWidth(
            palabra,
            fuente,
            tamano,
        )

        ancho_espacio = pdfmetrics.stringWidth(
            " ",
            fuente,
            tamano,
        )

        espacio = ancho_espacio if linea_actual else 0

        ancho_candidato = (
            ancho_actual
            + espacio
            + ancho_palabra
        )

        if ancho_candidato <= ancho:
            linea_actual.append((palabra, negrita))
            ancho_actual = ancho_candidato
        else:
            if linea_actual:
                lineas.append(linea_actual)

            linea_actual = [(palabra, negrita)]
            ancho_actual = ancho_palabra

    if linea_actual:
        lineas.append(linea_actual)

    for indice, linea in enumerate(lineas[:max_lineas]):
        posicion_x = x
        posicion_y = y - indice * interlineado

        for numero, (palabra, negrita) in enumerate(linea):
            fuente = (
                FUENTE_NEGRITA
                if negrita
                else FUENTE_NOMBRE
            )

            pdf.setFont(fuente, tamano)
            pdf.drawString(
                posicion_x,
                posicion_y,
                palabra,
            )

            posicion_x += pdfmetrics.stringWidth(
                palabra,
                fuente,
                tamano,
            )

            if numero < len(linea) - 1:
                posicion_x += pdfmetrics.stringWidth(
                    " ",
                    fuente,
                    tamano,
                )


# ============================================================
# GENERAR CONSTANCIA DE BAUTISMO
# ============================================================

def generar_constancia_bautismo(
    datos,
    observacion="",
    fecha_emision=None,
):
    """Genera la constancia de Bautismo sobre la plantilla institucional."""

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
    # 2. NOMBRE Y APELLIDOS DEL BAUTIZADO
    # --------------------------------------------------------

    nombre_completo = obtener_campo(
        datos,
        ("nombre_sacramentado",),
    )

    if not nombre_completo:
        nombre_completo = obtener_campo(
            datos,
            ("nombre", "nombre_bautizado", "nombre_completo"),
        )

    nombre, apellidos = separar_nombre(nombre_completo)

    nombre = nombre.upper()
    apellidos = apellidos.upper()

    # --------------------------------------------------------
    # 3. DATOS PERSONALES
    # --------------------------------------------------------

    fecha_nacimiento = obtener_dato(
        datos,
        ("fecha_nacimiento",),
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
        ("padre", "nombre_padre"),
    )

    madre = obtener_campo(
        datos,
        ("madre", "nombre_madre"),
    )

    padrino_1 = obtener_campo(
        datos,
        ("padrino_1", "nombre_padrino"),
    )

    padrino_2 = obtener_campo(
        datos,
        ("padrino_2", "nombre_madrina"),
    )

    padrinos = " y ".join(
        str(valor).strip()
        for valor in (padrino_1, padrino_2)
        if valor and str(valor).strip()
    )

    lugar_completo = ", ".join(
        str(valor).strip()
        for valor in (lugar_nacimiento, departamento)
        if valor and str(valor).strip()
    )

    # --------------------------------------------------------
    # 4. DATOS SACRAMENTALES
    # --------------------------------------------------------

    libro = numero_o_defecto(
        obtener_dato(datos, ("libro",))
    )

    folio = numero_o_defecto(
        obtener_dato(datos, ("folio",))
    )

    # El campo correcto para la partida es "partida".
    partida_valor = obtener_dato(
        datos,
        ("partida",),
    )

    partida = numero_o_na(
        partida_valor,
        defecto="N/A",
    )

    # Campos exactos de la tabla de Bautismos.
    fecha_bautismo_original = obtener_dato(
        datos,
        ("fecha_bautismo",),
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

    fecha_local = obtener_fecha_local(fecha_emision)

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
        pagesize=(ancho_pagina, alto_pagina),
    )

    pdf.setTitle("Certificado de Bautismo")

    # --------------------------------------------------------
    # 7. TEXTO DEL REGISTRO
    # --------------------------------------------------------


    segmentos_registro = [
        (
            "Que en el libro de Sacramentos de Bautismos No.",
            False,
        ),
        (str(libro), True),
        (", folio", False),
        (str(folio), True),
        (", partida No.", False),
        (str(partida), True),
        (
            ", en la cual se encuentra el registro del Bautismo de:",
            False,
        ),
    ]

    dibujar_texto_con_estilos(
        pdf,
        segmentos_registro,
        x=44,
        y=555,
        ancho=490,
        tamano=14,
        interlineado=18,
        max_lineas=3,
    )

    # --------------------------------------------------------
    # 8. DATOS PERSONALES
    # --------------------------------------------------------


    dibujar_texto_subrayado(
        pdf,
        nombre,
        x=240,
        y=494,
        tamano=14,
        negrita=True,
    )

    dibujar_texto_subrayado(
        pdf,
        apellidos,
        x=240,
        y=470,
        tamano=14,
        negrita=True,
    )

    campos_subrayados = [
        (fecha_nacimiento_texto, 240, 446),
        (lugar_completo, 240, 422),
        (padre, 240, 398),
        (madre, 240, 374),
        (padrinos, 240, 350),
        (fecha_bautismo_texto, 240, 326),
    ]

    for valor, x, y in campos_subrayados:
        if valor:
            dibujar_texto_subrayado_ajustado(
                pdf,
                valor,
                x=x,
                y=y,
                ancho=300,
                tamano=14,
                interlineado=17,
                max_lineas=2,
            )

    # --------------------------------------------------------
    # 9. TEXTO DE EXPEDICIÓN
    # --------------------------------------------------------
    # Solo el día, el mes y el año escrito en letras van en negrita.

    fecha_emision_convertida = convertir_fecha(fecha_local)

    if fecha_emision_convertida:
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

        dia = str(fecha_emision_convertida.day)
        mes = meses[fecha_emision_convertida.month - 1]
        anio = numero_a_letras(fecha_emision_convertida.year)

        segmentos_expedicion = [
            (
                "Para el uso que al interesado(a) convenga, "
                "se extiende en una hoja de papel bond "
                "membretada tamaño carta a los",
                False,
            ),
            (dia, True),
            ("días del mes de", False),
            (mes, True),
            ("del año", False),
            (anio, True),
            ("en la ciudad de Cobán, Alta Verapaz.", False),
        ]
    else:
        segmentos_expedicion = [
            (
                "Para el uso que al interesado(a) convenga, "
                "se extiende en una hoja de papel bond "
                "membretada tamaño carta, en la ciudad de "
                "Cobán, Alta Verapaz.",
                False,
            ),
        ]

    dibujar_texto_con_estilos(
        pdf,
        segmentos_expedicion,
        x=44,
        y=280,
        ancho=480,
        tamano=14,
        interlineado=18,
        max_lineas=4,
    )

    # --------------------------------------------------------
    # 10. OBSERVACIONES
    # --------------------------------------------------------

    dibujar_texto_ajustado(
        pdf,
        observacion,
        x=135,
        y=224,
        ancho=350,
        tamano=14,
        interlineado=17,
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

    pagina_plantilla.merge_page(pagina_overlay)

    writer = PdfWriter()
    writer.add_page(pagina_plantilla)

    resultado = io.BytesIO()

    writer.write(resultado)
    resultado.seek(0)

    buffer.close()

    return resultado