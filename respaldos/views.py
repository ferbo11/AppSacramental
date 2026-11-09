from functools import wraps

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import servicios


ROL_ADMINISTRADOR = 'administrador'


def _es_administrador(request):
    if getattr(request.user, 'is_superuser', False):
        return True

    rol = (
        request.session.get('rol_nombre')
        or ''
    ).strip().lower()

    return rol == ROL_ADMINISTRADOR


def administrador_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')

        if not _es_administrador(request):
            messages.error(
                request,
                'No tiene permisos para administrar los respaldos.',
            )
            return redirect('index')

        return view_func(request, *args, **kwargs)

    return wrapper


@administrador_requerido
@require_GET
def index(request):
    respaldos = servicios.listar_respaldos()

    total_bytes = sum(
        respaldo['tamano_bytes']
        for respaldo in respaldos
    )

    contexto = {
        'respaldos': respaldos,
        'total_respaldos': len(respaldos),
        'total_tamano': servicios.formatear_tamano(total_bytes),
        'ultimo_respaldo': respaldos[0] if respaldos else None,
        'retencion': servicios.retencion_actual(),
        'directorio': str(servicios.directorio_respaldos()),
        'herramientas': servicios.estado_herramientas(),
        'historial': servicios.leer_historial(100),
    }

    return render(
        request,
        'backups/index.html',
        contexto,
    )


@administrador_requerido
@require_POST
def crear(request):
    try:
        servicios.crear_respaldo(
            request.session.get('username'),
            tipo='manual',
        )
    except servicios.ErrorRespaldo as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            'Respaldo creado correctamente.',
        )

    return redirect('backups_index')


@administrador_requerido
@require_GET
def descargar(request, nombre):
    try:
        ruta = servicios.validar_ruta(nombre)
    except servicios.ErrorRespaldo as exc:
        messages.error(request, str(exc))
        return redirect('backups_index')

    if not ruta.exists():
        messages.error(
            request,
            'El respaldo seleccionado no existe.',
        )
        return redirect('backups_index')

    servicios.registrar_historial(
        request.session.get('username'),
        'DESCARGAR',
        'OK',
        'Respaldo descargado correctamente.',
        ruta.name,
    )

    return FileResponse(
        ruta.open('rb'),
        as_attachment=True,
        filename=ruta.name,
        content_type='application/octet-stream',
    )


@administrador_requerido
@require_POST
def eliminar(request):
    nombre = request.POST.get('nombre', '')

    try:
        servicios.eliminar_respaldo(
            nombre,
            request.session.get('username'),
        )
    except servicios.ErrorRespaldo as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            'Respaldo eliminado correctamente.',
        )

    return redirect('backups_index')


@administrador_requerido
@require_POST
def restaurar(request):
    nombre = request.POST.get('nombre', '')
    confirmacion = request.POST.get('confirmar', '')

    if confirmacion != '1':
        messages.error(
            request,
            (
                'Debe confirmar que comprende los riesgos antes '
                'de restaurar la base de datos.'
            ),
        )
        return redirect('backups_index')

    try:
        respaldo_seguridad = servicios.restaurar_respaldo(
            nombre,
            request.session.get('username'),
        )
    except servicios.ErrorRespaldo as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            (
                'Base de datos restaurada correctamente. '
                'Se creó el respaldo de seguridad '
                f'{respaldo_seguridad.name}.'
            ),
        )

    return redirect('backups_index')
