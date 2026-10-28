from collections.abc import Mapping
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.utils import timezone


MESES = (
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
)

ZONA_HORARIA_PARROQUIA = ZoneInfo('America/Guatemala')

UNIDADES = (
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
    'veintiuno',
    'veintidós',
    'veintitrés',
    'veinticuatro',
    'veinticinco',
    'veintiséis',
    'veintisiete',
    'veintiocho',
    'veintinueve',
)

DECENAS = {
    30: 'treinta',
    40: 'cuarenta',
    50: 'cincuenta',
    60: 'sesenta',
    70: 'setenta',
    80: 'ochenta',
    90: 'noventa',
}

CENTENAS = {
    100: 'cien',
    200: 'doscientos',
    300: 'trescientos',
    400: 'cuatrocientos',
    500: 'quinientos',
    600: 'seiscientos',
    700: 'setecientos',
    800: 'ochocientos',
    900: 'novecientos',
}


def numero_a_letras(numero):
    numero = int(numero)

    if numero < 0:
        return str(numero)

    if numero < len(UNIDADES):
        return UNIDADES[numero]

    if numero < 100:
        decena = (numero // 10) * 10
        resto = numero % 10

        if resto == 0:
            return DECENAS[decena]

        return f'{DECENAS[decena]} y {UNIDADES[resto]}'

    if numero < 1000:
        if numero == 100:
            return CENTENAS[100]

        centena = (numero // 100) * 100
        resto = numero % 100

        if resto == 0:
            return CENTENAS[centena]

        return f'{CENTENAS[centena]} {numero_a_letras(resto)}'

    if numero < 1000000:
        miles = numero // 1000
        resto = numero % 1000

        if miles == 1:
            texto = 'mil'
        else:
            texto = f'{numero_a_letras(miles)} mil'

        if resto:
            texto = f'{texto} {numero_a_letras(resto)}'

        return texto

    return str(numero)


def convertir_a_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    if isinstance(valor, str):
        valor = valor.strip()

        for formato in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                return datetime.strptime(valor, formato).date()
            except ValueError:
                continue

    return None


def formatear_fecha_larga(fecha, anio_en_letras=True):
    fecha = convertir_a_fecha(fecha)

    if fecha is None:
        return (
            'a los ____ días del mes de '
            '__________ del año ____'
        )

    anio = (
        numero_a_letras(fecha.year)
        if anio_en_letras
        else str(fecha.year)
    )

    return (
        f'a los {fecha.day} días del mes de '
        f'{MESES[fecha.month - 1]} del año {anio}'
    )


def obtener_fecha_local(ahora=None):
    if ahora is None:
        ahora = timezone.now()

    if isinstance(ahora, datetime):
        if timezone.is_naive(ahora):
            ahora = ahora.replace(
                tzinfo=ZONA_HORARIA_PARROQUIA
            )

        return ahora.astimezone(
            ZONA_HORARIA_PARROQUIA
        )

    if isinstance(ahora, date):
        return datetime.combine(
            ahora,
            time.min,
            tzinfo=ZONA_HORARIA_PARROQUIA,
        )

    raise TypeError(
        'La fecha debe ser un objeto date, datetime o None.'
    )


def obtener_fecha_emision(ahora=None):
    fecha_local = obtener_fecha_local(ahora)

    return formatear_fecha_larga(
        fecha_local
    )


def obtener_dato(datos, claves, defecto=None):
    if datos is None:
        return defecto

    if isinstance(datos, Mapping):
        for clave in claves:
            if clave not in datos:
                continue

            valor = datos[clave]

            if valor is not None and valor != '':
                return valor

        return defecto

    for clave in claves:
        valor = getattr(datos, clave, None)

        if valor is not None and valor != '':
            return valor

    return defecto


def texto_o_defecto(valor, defecto='____'):
    if valor is None:
        return defecto

    texto = str(valor).strip()

    return texto or defecto


def numero_o_defecto(valor, defecto='____'):
    if valor is None or valor == '':
        return defecto

    try:
        if isinstance(valor, bool):
            return str(int(valor))
        num = int(valor)
        return str(num)
    except (TypeError, ValueError):
        return texto_o_defecto(valor, defecto)


def numero_o_na(valor, defecto='N/A'):
    if valor is None or valor == '':
        return defecto
    try:
        if isinstance(valor, bool):
            return str(int(valor))
        # If it's 0, respect it as valid value per requirement
        num = int(valor)
        return str(num)
    except (TypeError, ValueError):
        s = str(valor).strip()
        return s if s else defecto


def valor_o_na(valor):
    if valor is None or valor == '':
        return 'N/A'
    try:
        # Don't treat 0 as missing unless explicitly documented otherwise
        if isinstance(valor, bool):
            return str(int(valor))
        # Convert numbers to string for presentation
        if isinstance(valor, int) and not isinstance(valor, bool):
            return str(valor)
        if isinstance(valor, float):
            # If it's a whole number, maybe present as int string
            if valor.is_integer():
                return str(int(valor))
            return str(valor)
        # Try to parse as int
        # If it's numeric string representing int
        s = str(valor).strip()
        if s == '':
            return 'N/A'
        # Check if it's all digits (possibly negative)
        return s
    except Exception:
        s = str(valor).strip()
        return s if s else 'N/A'
