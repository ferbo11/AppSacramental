from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse

from .models import Bautismo
from constancias.models import Constancia
from constancias.generador_bautismo import generar_constancia_bautismo
from historial.models import ConstanciaEmitida


def buscar_bautismo(request):
    nombre = request.GET.get('nombre', '').strip()
    apellidos = request.GET.get('apellidos', '').strip()

    resultados = Bautismo.objects.all()

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
        'bautismo/bautismo.html',
        {
            'resultados': resultados,
            'nombre': nombre,
            'apellidos': apellidos,
            'busqueda_realizada': bool(nombre or apellidos),
        }
    )


def generar_pdf_bautismo(request, id_bautismo):

    if request.method != 'POST':
        return redirect('bautismo')

    try:
        bautismo = Bautismo.objects.get(id=id_bautismo)
    except Exception:
        try:
            bautismo = get_object_or_404(Bautismo, pk=id_bautismo)
        except Exception:
            return redirect('bautismo')

    observacion = request.POST.get('observacion', '').strip()
    if not observacion:
        observacion = 'NINGUNA'

    ultima_constancia = (
        Constancia.objects
        .filter(tipo_sacramento='Bautismo')
        .order_by('-numero_partida')
        .first()
    )

    if ultima_constancia and ultima_constancia.numero_partida is not None:
        numero_partida = ultima_constancia.numero_partida + 1
    else:
        numero_partida = 1

    datos = {
        'nombre_sacramentado': bautismo.nombre_sacramentado,
        'padre': bautismo.padre,
        'madre': bautismo.madre,
        'padrino_1': bautismo.padrino_1,
        'padrino_2': bautismo.padrino_2,
        'lugar_nacimiento': bautismo.lugar_nacimiento,
        'departamento': bautismo.departamento,
        'libro': bautismo.libro,
        'folio': bautismo.folio,
    }

    try:
        datos['numero_partida'] = numero_partida
    except Exception:
        pass

    pdf = generar_constancia_bautismo(datos, observacion=observacion)

    nombre_archivo = (
        f'bautismo_{numero_partida:03d}_{(bautismo.nombre_sacramentado or "").replace(" ", "_")}.pdf'
    )

    constancia = Constancia(
        tipo_sacramento='Bautismo',
        numero_partida=numero_partida,
        id_registro=bautismo.id,
        nombre_persona=bautismo.nombre_sacramentado or getattr(bautismo, 'nombre', ''),
        usuario_emisor=request.session.get('username'),
        observaciones=observacion
    )

    constancia.archivo_pdf.save(nombre_archivo, pdf, save=True)

    try:
        ConstanciaEmitida.objects.using('historial').create(
            nombre=(bautismo.nombre_sacramentado or '')[:200],
            sacramento='bautismo',
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

from AppSacramental.views import usuario_requerido
from .forms import BautismoForm


@usuario_requerido
def listar_bautismos(request):
    consulta = request.GET.get('q', '').strip()
    resultados = Bautismo.objects.all()
    if consulta:
        from django.db.models import Q
        resultados = resultados.filter(
            Q(nombre_sacramentado__icontains=consulta) |
            Q(padre__icontains=consulta) |
            Q(madre__icontains=consulta) |
            Q(lugar_nacimiento__icontains=consulta) |
            Q(departamento__icontains=consulta)
        )
    resultados = resultados.order_by('-id')
    paginator = Paginator(resultados, 10)
    pagina = request.GET.get('pagina')
    page_obj = paginator.get_page(pagina)
    return render(request, 'sacramentos/listar_bautismos.html', {
        'page_obj': page_obj,
        'consulta': consulta,
        'total': resultados.count(),
    })


@usuario_requerido
def crear_bautismo(request):
    if request.method == 'POST':
        formulario = BautismoForm(request.POST)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de bautismo creado correctamente.')
                return redirect('listar_bautismos')
            except Exception as e:
                messages.error(request, 'No se pudo crear el registro de bautismo.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = BautismoForm()
    return render(request, 'sacramentos/formulario_bautismo.html', {'formulario': formulario, 'accion': 'Crear'})


@usuario_requerido
def ver_bautismo(request, pk):
    registro = get_object_or_404(Bautismo, pk=pk)
    return render(request, 'sacramentos/ver_bautismo.html', {'registro': registro})


@usuario_requerido
def editar_bautismo(request, pk):
    registro = get_object_or_404(Bautismo, pk=pk)
    if request.method == 'POST':
        formulario = BautismoForm(request.POST, instance=registro)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Registro de bautismo actualizado correctamente.')
                return redirect('ver_bautismo', pk=registro.pk)
            except Exception as e:
                messages.error(request, 'No se pudo actualizar el registro de bautismo.')
        else:
            messages.error(request, 'Revise los datos del formulario.')
    else:
        formulario = BautismoForm(instance=registro)
    return render(request, 'sacramentos/formulario_bautismo.html', {'formulario': formulario, 'accion': 'Editar', 'registro': registro})


@usuario_requerido
def eliminar_bautismo(request, pk):
    registro = get_object_or_404(Bautismo, pk=pk)
    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(request, 'Registro de bautismo eliminado correctamente.')
            return redirect('listar_bautismos')
        except Exception as e:
            messages.error(request, 'No se pudo eliminar el registro de bautismo.')
    return render(request, 'sacramentos/eliminar_bautismo.html', {'registro': registro})
