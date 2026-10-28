from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse

from .models import Confirmacion

from constancias.models import Constancia
from constancias.generador_confirmacion import generar_constancia_confirmacion

from historial.models import ConstanciaEmitida


def buscar_confirmacion(request):

    nombre = request.GET.get('nombre', '').strip()
    apellidos = request.GET.get('apellidos', '').strip()

    resultados = Confirmacion.objects.all()

    if nombre or apellidos:
        query = nombre or apellidos
        try:
            resultados = resultados.filter(nombre_sacramentado__icontains=query)
        except Exception:
            try:
                resultados = resultados.filter(nombre__icontains=query)
            except Exception:
                pass

    return render(
        request,
        'confirmacion/confirmacion.html',
        {
            'resultados': resultados,
            'nombre': nombre,
            'apellidos': apellidos,
            'busqueda_realizada': bool(nombre or apellidos),
        }
    )


def generar_pdf_confirmacion(request, id_confirmacion):

    if request.method != 'POST':
        return redirect('confirmacion')

    try:
        confirmacion = Confirmacion.objects.get(id=id_confirmacion)
    except Exception:
        try:
            confirmacion = get_object_or_404(
                Confirmacion,
                id_confirmacion=id_confirmacion
            )
        except Exception:
            confirmacion = get_object_or_404(
                Confirmacion,
                pk=id_confirmacion
            )

    observacion = request.POST.get(
        'observacion',
        ''
    ).strip()

    if not observacion:
        observacion = 'NINGUNA'

    ultima_constancia = (
        Constancia.objects
        .filter(
            tipo_sacramento='Confirmación'
        )
        .order_by('-numero_partida')
        .first()
    )

    if ultima_constancia:
        numero_partida = (
            ultima_constancia.numero_partida + 1
        )
    else:
        numero_partida = 1

    pdf = generar_constancia_confirmacion(
        confirmacion,
        numero_partida,
        observacion
    )

    nombre_archivo = (
        f'confirmacion_'
        f'{numero_partida:03d}_'
        f'{confirmacion.nombre.replace(" ", "_")}.pdf'
    )

    constancia = Constancia(
        tipo_sacramento='Confirmación',
        numero_partida=numero_partida,
        id_registro=confirmacion.id_confirmacion,
        nombre_persona=confirmacion.nombre,
        usuario_emisor=request.session.get('username'),
        observaciones=observacion
    )

    constancia.archivo_pdf.save(
        nombre_archivo,
        pdf,
        save=True
    )

    ConstanciaEmitida.objects.using('historial').create(
        nombre=confirmacion.nombre[:200],
        sacramento='confirmacion',
        usuario=(
            request.session.get('username')
            or 'Desconocido'
        )[:150],
    )

    return FileResponse(
        constancia.archivo_pdf.open('rb'),
        as_attachment=False,
        filename=nombre_archivo,
        content_type='application/pdf'
    )

from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from AppSacramental.views import usuario_requerido
from .forms import ConfirmacionForm


@usuario_requerido
def listar_confirmaciones(request):
    consulta = request.GET.get('q', '').strip()
    resultados = Confirmacion.objects.all()
    if consulta:
        resultados = resultados.filter(
            Q(nombre_sacramentado__icontains=consulta) |
            Q(padre__icontains=consulta) |
            Q(madre__icontains=consulta)
        )
    resultados = resultados.order_by('-id')
    paginator = Paginator(resultados, 10)
    pagina = request.GET.get('pagina')
    page_obj = paginator.get_page(pagina)
    return render(request, 'sacramentos/listar_confirmaciones.html', {
        'page_obj': page_obj,
        'consulta': consulta,
        'total': paginator.count,
    })


@usuario_requerido
def crear_confirmacion(request):
    if request.method == 'POST':
        formulario = ConfirmacionForm(request.POST)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de confirmación creado correctamente.')
                return redirect('listar_confirmaciones')
            except Exception:
                messages.error(request, 'No se pudo crear el registro de confirmación.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = ConfirmacionForm()
    return render(request, 'sacramentos/formulario_confirmacion.html', {'formulario': formulario, 'accion': 'Crear'})


@usuario_requerido
def ver_confirmacion(request, pk):
    registro = get_object_or_404(Confirmacion, pk=pk)
    return render(request, 'sacramentos/ver_confirmacion.html', {'registro': registro})


@usuario_requerido
def editar_confirmacion(request, pk):
    registro = get_object_or_404(Confirmacion, pk=pk)
    if request.method == 'POST':
        formulario = ConfirmacionForm(request.POST, instance=registro)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de confirmación actualizado correctamente.')
                return redirect('ver_confirmacion', pk=registro.pk)
            except Exception:
                messages.error(request, 'No se pudo actualizar el registro de confirmación.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = ConfirmacionForm(instance=registro)
    return render(request, 'sacramentos/formulario_confirmacion.html', {'formulario': formulario, 'accion': 'Editar', 'registro': registro})


@usuario_requerido
def eliminar_confirmacion(request, pk):
    registro = get_object_or_404(Confirmacion, pk=pk)
    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(request, 'Registro de confirmación eliminado correctamente.')
            return redirect('listar_confirmaciones')
        except Exception:
            messages.error(request, 'No se pudo eliminar el registro de confirmación.')
    return render(request, 'sacramentos/eliminar_confirmacion.html', {'registro': registro})
