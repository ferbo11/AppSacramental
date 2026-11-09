import json
import os
import re
import secrets
import shutil
import subprocess

from datetime import datetime, timezone as dt_timezone
from pathlib import Path

from django.conf import settings
from django.db import connections
from django.utils import timezone


NOMBRE_HISTORIAL = 'historial_respaldos.jsonl'
PATRON_NOMBRE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*\.dump$')

TIPOS_RESPALDO = {
    'manual': 'Manual',
    'pre_restauracion': 'Pre-restauración',
}


class ErrorRespaldo(Exception):
    pass


def directorio_respaldos():
    ruta = Path(
        getattr(
            settings,
            'BACKUP_DIR',
            settings.BASE_DIR / 'backups',
        )
    )

    ruta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return ruta


def retencion_actual():
    try:
        retencion = int(
            getattr(
                settings,
                'BACKUP_RETENTION',
                15,
            )
        )
    except (TypeError, ValueError):
        return 15

    return max(retencion, 0)


def _validar_motor():
    if settings.DB_ENGINE not in {'postgresql', 'postgres'}:
        raise ErrorRespaldo(
            'El módulo de respaldos está configurado para PostgreSQL.'
        )


def _entorno_postgres():
    entorno = os.environ.copy()

    entorno.update(
        {
            'PGHOST': settings.DB_HOST,
            'PGPORT': str(settings.DB_PORT),
            'PGUSER': settings.DB_USER,
            'PGPASSWORD': settings.DB_PASSWORD,
            'PGDATABASE': settings.DB_NAME,
            'PGCONNECT_TIMEOUT': '10',
        }
    )

    return entorno


def _detalle_resultado(resultado):
    texto = (
        resultado.stderr
        or resultado.stdout
        or ''
    ).strip()

    texto = re.sub(
        r'password=\S+',
        'password=***',
        texto,
        flags=re.IGNORECASE,
    )

    if texto:
        return texto[-800:]

    return f'código de salida {resultado.returncode}'


def _ejecutar(comando, timeout=900):
    try:
        return subprocess.run(
            comando,
            env=_entorno_postgres(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ErrorRespaldo(
            'No se encontró la herramienta de PostgreSQL necesaria.'
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ErrorRespaldo(
            'La operación de PostgreSQL excedió el tiempo máximo permitido.'
        ) from exc


def _fecha_local(timestamp):
    fecha = datetime.fromtimestamp(
        timestamp,
        tz=dt_timezone.utc,
    )

    return timezone.localtime(fecha)


def formatear_tamano(bytes_totales):
    valor = float(bytes_totales)

    for unidad in ('B', 'KB', 'MB', 'GB', 'TB'):
        if valor < 1024 or unidad == 'TB':
            if unidad == 'B':
                return f'{int(valor)} B'

            return f'{valor:.1f} {unidad}'

        valor /= 1024

    return f'{bytes_totales} B'


def _tipo_respaldo(nombre):
    for clave, etiqueta in TIPOS_RESPALDO.items():
        if f'sacranet_{clave}_' in nombre:
            return etiqueta

    return 'Otro'


def validar_ruta(nombre):
    nombre = str(nombre or '').strip()

    if not PATRON_NOMBRE.fullmatch(nombre):
        raise ErrorRespaldo(
            'El nombre del respaldo no es válido.'
        )

    directorio = directorio_respaldos().resolve()
    ruta = (directorio / nombre).resolve()

    if ruta.parent != directorio:
        raise ErrorRespaldo(
            'La ruta del respaldo no es válida.'
        )

    return ruta


def listar_respaldos():
    directorio = directorio_respaldos()
    respaldos = []

    for ruta in directorio.iterdir():
        if not ruta.is_file():
            continue

        if not PATRON_NOMBRE.fullmatch(ruta.name):
            continue

        try:
            informacion = ruta.stat()
        except OSError:
            continue

        fecha = _fecha_local(informacion.st_mtime)

        respaldos.append(
            {
                'nombre': ruta.name,
                'tipo': _tipo_respaldo(ruta.name),
                'fecha': fecha,
                'fecha_texto': fecha.strftime('%d/%m/%Y %H:%M'),
                'tamano_bytes': informacion.st_size,
                'tamano': formatear_tamano(informacion.st_size),
                'estado': (
                    'Disponible'
                    if informacion.st_size > 0
                    else 'Vacío'
                ),
            }
        )

    respaldos.sort(
        key=lambda respaldo: respaldo['fecha'],
        reverse=True,
    )

    return respaldos


def registrar_historial(
    usuario,
    accion,
    resultado,
    mensaje='',
    archivo='',
):
    directorio = directorio_respaldos()
    entrada = {
        'fecha': timezone.localtime().isoformat(timespec='seconds'),
        'usuario': str(usuario or 'sistema')[:150],
        'accion': str(accion),
        'resultado': str(resultado),
        'archivo': str(archivo or ''),
        'mensaje': str(mensaje or '')[:1000],
    }

    try:
        with (directorio / NOMBRE_HISTORIAL).open(
            'a',
            encoding='utf-8',
        ) as archivo_historial:
            archivo_historial.write(
                json.dumps(
                    entrada,
                    ensure_ascii=False,
                )
                + '\n'
            )
    except OSError:
        pass


def leer_historial(limite=100):
    directorio = directorio_respaldos()
    ruta = directorio / NOMBRE_HISTORIAL

    if not ruta.exists():
        return []

    try:
        lineas = ruta.read_text(
            encoding='utf-8',
            errors='replace',
        ).splitlines()
    except OSError:
        return []

    entradas = []

    for linea in reversed(lineas[-limite:]):
        try:
            entrada = json.loads(linea)
        except (TypeError, ValueError):
            continue

        fecha = str(entrada.get('fecha', ''))

        try:
            fecha_dt = datetime.fromisoformat(fecha)
            entrada['fecha_texto'] = fecha_dt.strftime(
                '%d/%m/%Y %H:%M'
            )
        except ValueError:
            entrada['fecha_texto'] = fecha

        entrada.setdefault('usuario', 'sistema')
        entrada.setdefault('accion', '')
        entrada.setdefault('resultado', '')
        entrada.setdefault('archivo', '')
        entrada.setdefault('mensaje', '')

        entradas.append(entrada)

    return entradas


def _informacion_herramienta(nombre):
    ruta = shutil.which(nombre)

    if not ruta:
        return {
            'disponible': False,
            'ruta': '',
            'version': '',
        }

    version = ''

    try:
        resultado = subprocess.run(
            [ruta, '--version'],
            capture_output=True,
            text=True,
            timeout=20,
        )
        version = (
            resultado.stdout
            or resultado.stderr
            or ''
        ).strip()
    except (OSError, subprocess.TimeoutExpired):
        version = ''

    return {
        'disponible': True,
        'ruta': ruta,
        'version': version,
    }


def estado_herramientas():
    return {
        'pg_dump': _informacion_herramienta('pg_dump'),
        'pg_restore': _informacion_herramienta('pg_restore'),
    }


def aplicar_retencion():
    retencion = retencion_actual()

    if retencion <= 0:
        return []

    respaldos = listar_respaldos()

    if len(respaldos) <= retencion:
        return []

    directorio = directorio_respaldos()
    eliminados = []

    for respaldo in respaldos[retencion:]:
        ruta = directorio / respaldo['nombre']

        try:
            ruta.unlink()
        except OSError:
            continue

        eliminados.append(respaldo['nombre'])
        registrar_historial(
            'sistema',
            'RETENCION',
            'OK',
            (
                'Respaldo eliminado automáticamente por la '
                f'política de conservación de {retencion} copias.'
            ),
            respaldo['nombre'],
        )

    return eliminados


def crear_respaldo(usuario, tipo='manual'):
    _validar_motor()

    pg_dump = shutil.which('pg_dump')
    pg_restore = shutil.which('pg_restore')

    if not pg_dump or not pg_restore:
        raise ErrorRespaldo(
            'No se encontraron pg_dump y pg_restore. '
            'Verifique la instalación del cliente de PostgreSQL.'
        )

    directorio = directorio_respaldos()
    token = secrets.token_hex(3)
    fecha = timezone.localtime().strftime('%Y%m%d_%H%M%S')
    nombre = f'sacranet_{tipo}_{fecha}_{token}.dump'
    destino = directorio / nombre
    temporal = directorio / f'.{nombre}.tmp'

    try:
        resultado = _ejecutar(
            [
                pg_dump,
                '--format=custom',
                '--no-owner',
                '--no-privileges',
                '--file',
                str(temporal),
            ],
            timeout=900,
        )

        if resultado.returncode != 0:
            raise ErrorRespaldo(
                'pg_dump no pudo generar el respaldo: '
                f'{_detalle_resultado(resultado)}'
            )

        if (
            not temporal.exists()
            or temporal.stat().st_size == 0
        ):
            raise ErrorRespaldo(
                'El respaldo generado está vacío.'
            )

        verificacion = _ejecutar(
            [pg_restore, '--list', str(temporal)],
            timeout=120,
        )

        if verificacion.returncode != 0:
            raise ErrorRespaldo(
                'El respaldo generado no pudo verificarse: '
                f'{_detalle_resultado(verificacion)}'
            )

        os.replace(
            temporal,
            destino,
        )
    except ErrorRespaldo as exc:
        if temporal.exists():
            temporal.unlink(missing_ok=True)

        registrar_historial(
            usuario,
            'CREAR',
            'ERROR',
            str(exc),
            nombre,
        )
        raise
    except OSError as exc:
        if temporal.exists():
            temporal.unlink(missing_ok=True)

        mensaje = f'No se pudo guardar el respaldo: {exc}'
        registrar_historial(
            usuario,
            'CREAR',
            'ERROR',
            mensaje,
            nombre,
        )
        raise ErrorRespaldo(mensaje) from exc

    try:
        aplicar_retencion()
    except Exception:
        pass

    registrar_historial(
        usuario,
        'CREAR',
        'OK',
        f'Respaldo {tipo} creado correctamente.',
        nombre,
    )

    return destino


def eliminar_respaldo(nombre, usuario):
    ruta = validar_ruta(nombre)

    if not ruta.exists():
        raise ErrorRespaldo(
            'El respaldo seleccionado no existe.'
        )

    try:
        ruta.unlink()
    except OSError as exc:
        mensaje = f'No se pudo eliminar el respaldo: {exc}'
        registrar_historial(
            usuario,
            'ELIMINAR',
            'ERROR',
            mensaje,
            ruta.name,
        )
        raise ErrorRespaldo(mensaje) from exc

    registrar_historial(
        usuario,
        'ELIMINAR',
        'OK',
        'Respaldo eliminado correctamente.',
        ruta.name,
    )


def restaurar_respaldo(nombre, usuario):
    _validar_motor()

    ruta = validar_ruta(nombre)

    if (
        not ruta.exists()
        or ruta.stat().st_size == 0
    ):
        raise ErrorRespaldo(
            'El respaldo seleccionado no existe o está vacío.'
        )

    pg_restore = shutil.which('pg_restore')

    if not pg_restore:
        raise ErrorRespaldo(
            'No se encontró pg_restore. Verifique la '
            'instalación del cliente de PostgreSQL.'
        )

    verificacion = _ejecutar(
        [pg_restore, '--list', str(ruta)],
        timeout=120,
    )

    if verificacion.returncode != 0:
        raise ErrorRespaldo(
            'El archivo no es un respaldo válido de PostgreSQL: '
            f'{_detalle_resultado(verificacion)}'
        )

    try:
        respaldo_seguridad = crear_respaldo(
            usuario,
            tipo='pre_restauracion',
        )
    except ErrorRespaldo as exc:
        raise ErrorRespaldo(
            'No se pudo crear el respaldo de seguridad antes '
            f'de restaurar: {exc}'
        ) from exc

    try:
        connections.close_all()

        resultado = _ejecutar(
            [
                pg_restore,
                '--clean',
                '--if-exists',
                '--no-owner',
                '--no-privileges',
                '--single-transaction',
                '--exit-on-error',
                '--dbname',
                settings.DB_NAME,
                str(ruta),
            ],
            timeout=1800,
        )

        if resultado.returncode != 0:
            raise ErrorRespaldo(
                'pg_restore no pudo restaurar el respaldo: '
                f'{_detalle_resultado(resultado)}'
            )

        connections.close_all()
    except ErrorRespaldo as exc:
        connections.close_all()
        registrar_historial(
            usuario,
            'RESTAURAR',
            'ERROR',
            str(exc),
            ruta.name,
        )
        raise
    except Exception as exc:
        connections.close_all()
        mensaje = f'No se pudo restaurar el respaldo: {exc}'
        registrar_historial(
            usuario,
            'RESTAURAR',
            'ERROR',
            mensaje,
            ruta.name,
        )
        raise ErrorRespaldo(mensaje) from exc

    registrar_historial(
        usuario,
        'RESTAURAR',
        'OK',
        (
            'Base de datos restaurada correctamente. '
            'Respaldo de seguridad: '
            f'{respaldo_seguridad.name}'
        ),
        ruta.name,
    )

    return respaldo_seguridad
