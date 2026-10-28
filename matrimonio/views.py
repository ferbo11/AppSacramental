from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse

from .models import Matrimonio
from constancias.models import Constancia
from constancias.generador_matrimonio import generar_constancia_matrimonio
from historial.models import ConstanciaEmitida


def buscar_matrimonio(request):

    esposo = request.GET.get('esposo', '').strip()
    esposa = request.GET.get('esposa', '').strip()

    resultados = Matrimonio.objects.all()

    if esposo:
        try:
            resultados = resultados.filter(esposo__icontains=esposo)
        except Exception:
            try:
                resultados = resultados.filter(nombre_esposo__icontains=esposo)
            except Exception:
                pass

    if esposa:
        try:
            resultados = resultados.filter(esposa__icontains=esposa)
        except Exception:
            try:
                resultados = resultados.filter(nombre_esposa__icontains=esposa)
            except Exception:
                pass

    return render(
        request,
        'matrimonio/matrimonio.html',
        {
            'resultados': resultados,
            'esposo': esposo,
            'esposa': esposa,
            'busqueda_realizada': bool(esposo or esposa),
        }
    )


def generar_pdf_matrimonio(request, id_matrimonio):

    if request.method != 'POST':
        return redirect('matrimonio')

    try:
        matrimonio = Matrimonio.objects.get(id=id_matrimonio)
    except Exception:
        try:
            matrimonio = get_object_or_404(Matrimonio, pk=id_matrimonio)
        except Exception:
            return redirect('matrimonio')

    observacion = request.POST.get('observacion', '').strip()
    if not observacion:
        observacion = 'NINGUNA'

    ultima_constancia = (
        Constancia.objects
        .filter(tipo_sacramento='Matrimonio')
        .order_by('-numero_partida')
        .first()
    )

    if ultima_constancia and ultima_constancia.numero_partida is not None:
        numero_partida = ultima_constancia.numero_partida + 1
    else:
        numero_partida = 1

    datos = {
        'nombre_esposo': matrimonio.esposo or getattr(matrimonio, 'nombre_esposo', ''),
        'nombre_esposa': matrimonio.esposa or getattr(matrimonio, 'nombre_esposa', ''),
        'libro': matrimonio.libro,
        'folio': matrimonio.folio,
        'anio': matrimonio.ano or getattr(matrimonio, 'anio', None),
    }

    pdf = generar_constancia_matrimonio(datos, observacion=observacion)

    nombre_archivo = (
        f'matrimonio_{numero_partida:03d}_{(matrimonio.esposo or "matrimonio").replace(" ", "_")}.pdf'
    )

    constancia = Constancia(
        tipo_sacramento='Matrimonio',
        numero_partida=numero_partida,
        id_registro=matrimonio.id,
        nombre_persona=f"{matrimonio.esposo or ''} y {matrimonio.esposa or ''}".strip(),
        usuario_emisor=request.session.get('username'),
        observaciones=observacion
    )

    constancia.archivo_pdf.save(nombre_archivo, pdf, save=True)

    try:
        ConstanciaEmitida.objects.using('historial').create(
            nombre=f"{matrimonio.esposo or ''} y {matrimonio.esposa or ''}".strip()[:200],
            sacramento='matrimonio',
            usuario=(request.session.get('username') or 'Desconocido')[:150],
        )
    except Exception:
        pass

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
from .forms import MatrimonioForm


@usuario_requerido
def listar_matrimonios(request):
    consulta = request.GET.get('q', '').strip()
    resultados = Matrimonio.objects.all()
    if consulta:
        resultados = resultados.filter(
            Q(esposo__icontains=consulta) |
            Q(esposa__icontains=consulta) |
            Q(libro__icontains=consulta)
        )
    resultados = resultados.order_by('-id')
    paginator = Paginator(resultados, 10)
    pagina = request.GET.get('pagina')
    page_obj = paginator.get_page(pagina)
    return render(request, 'sacramentos/listar_matrimonios.html', {
        'page_obj': page_obj,
        'consulta': consulta,
        'total': paginator.count,
    })


@usuario_requerido
def crear_matrimonio(request):
    if request.method == 'POST':
        formulario = MatrimonioForm(request.POST)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de matrimonio creado correctamente.')
                return redirect('listar_matrimonios')
            except Exception:
                messages.error(request, 'No se pudo crear el registro de matrimonio.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = MatrimonioForm()
    return render(request, 'sacramentos/formulario_matrimonio.html', {'formulario': formulario, 'accion': 'Crear'})


@usuario_requerido
def ver_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)
    return render(request, 'sacramentos/ver_matrimonio.html', {'registro': registro})


@usuario_requerido
def editar_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)
    if request.method == 'POST':
        formulario = MatrimonioForm(request.POST, instance=registro)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de matrimonio actualizado correctamente.')
                return redirect('ver_matrimonio', pk=registro.pk)
            except Exception:
                messages.error(request, 'No se pudo actualizar el registro de matrimonio.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = MatrimonioForm(instance=registro)
    return render(request, 'sacramentos/formulario_matrimonio.html', {'formulario': formulario, 'accion': 'Editar', 'registro': registro})


@usuario_requerido
def eliminar_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)
    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(request, 'Registro de matrimonio eliminado correctamente.')
            return redirect('listar_matrimonios')
        except Exception:
            messages.error(request, 'No se pudo eliminar el registro de matrimonio.')
    return render(request, 'sacramentos/eliminar_matrimonio.html', {'registro': registro})
