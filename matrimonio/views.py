import re

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from AppSacramental.views import usuario_requerido
from constancias.generador_matrimonio import generar_constancia_matrimonio
from constancias.models import Constancia
from historial.models import ConstanciaEmitida

from .forms import MatrimonioForm
from .models import Matrimonio


def _texto(valor):
    return (valor or '').strip()


def _entero(valor):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def _url_retorno(request):
    volver = request.POST.get('volver', '')

    if volver.startswith('/') and not volver.startswith('//'):
        return volver

    return reverse('matrimonio')


def buscar_matrimonio(request):
    esposo = _texto(request.GET.get('esposo'))
    esposa = _texto(request.GET.get('esposa'))
    libro = _texto(request.GET.get('libro'))
    folio = _texto(request.GET.get('folio'))
    ano = _texto(request.GET.get('ano'))

    errores_busqueda = []
    busqueda_realizada = any((esposo, esposa, libro, folio, ano))

    resultados = Matrimonio.objects.none()

    if busqueda_realizada:
        resultados = Matrimonio.objects.all()

        if esposo:
            resultados = resultados.filter(esposo__icontains=esposo)

        if esposa:
            resultados = resultados.filter(esposa__icontains=esposa)

        if libro:
            resultados = resultados.filter(libro__icontains=libro)

        if folio:
            folio_numero = _entero(folio)

            if folio_numero is None:
                errores_busqueda.append(
                    'El folio debe ser un número entero.'
                )
            else:
                resultados = resultados.filter(folio=folio_numero)

        if ano:
            ano_numero = _entero(ano)

            if ano_numero is None:
                errores_busqueda.append(
                    'El año debe ser un número entero.'
                )
            else:
                resultados = resultados.filter(ano=ano_numero)

        if errores_busqueda:
            resultados = Matrimonio.objects.none()
        else:
            resultados = resultados.order_by(
                'esposo',
                'esposa',
                'ano',
                'id',
            )

    return render(
        request,
        'matrimonio/matrimonio.html',
        {
            'resultados': resultados,
            'esposo': esposo,
            'esposa': esposa,
            'libro': libro,
            'folio': folio,
            'ano': ano,
            'errores_busqueda': errores_busqueda,
            'busqueda_realizada': busqueda_realizada,
        }
    )


def generar_pdf_matrimonio(request, id_matrimonio):
    if request.method != 'POST':
        return redirect('matrimonio')

    id_seleccionado = request.POST.get('matrimonio_id')

    if str(id_seleccionado).strip() != str(id_matrimonio):
        messages.error(
            request,
            'El matrimonio seleccionado no corresponde al registro '
            'consultado. Vuelva a realizar la búsqueda.',
        )
        return redirect(_url_retorno(request))

    matrimonio = Matrimonio.objects.filter(pk=id_matrimonio).first()

    if matrimonio is None:
        messages.error(
            request,
            'No se encontraron matrimonios con el identificador '
            'seleccionado. Vuelva a realizar la búsqueda.',
        )
        return redirect(_url_retorno(request))

    requiere_confirmacion = (
        bool(matrimonio.requiere_revision)
        or bool(matrimonio.datos_faltantes)
    )

    if (
        requiere_confirmacion
        and request.POST.get('confirmar_datos') != '1'
    ):
        if matrimonio.requiere_revision:
            messages.warning(
                request,
                'Este matrimonio está marcado para revisión. '
                'Confirme que revisó los datos antes de generar '
                'la constancia.',
            )

        if matrimonio.datos_faltantes:
            messages.warning(
                request,
                'Faltan datos importantes en el registro: '
                f'{", ".join(matrimonio.datos_faltantes)}.',
            )

        return redirect(_url_retorno(request))

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
        'id': matrimonio.id,
        'nombre_esposo': matrimonio.esposo,
        'esposo': matrimonio.esposo,
        'edad_esposo': matrimonio.edad_esposo,
        'nombre_esposa': matrimonio.esposa,
        'esposa': matrimonio.esposa,
        'edad_esposa': matrimonio.edad_esposa,
        'padre_esposo': matrimonio.padre_esposo,
        'madre_esposo': matrimonio.madre_esposo,
        'padre_esposa': matrimonio.padre_esposa,
        'madre_esposa': matrimonio.madre_esposa,
        'testigo_1': matrimonio.testigo_1,
        'testigo_2': matrimonio.testigo_2,
        'libro': matrimonio.libro,
        'folio': matrimonio.folio,
        'ano': matrimonio.ano,
        'anio': matrimonio.ano,
        'mes': matrimonio.mes,
        'dia': matrimonio.dia,
        'fecha_matrimonio': matrimonio.fecha_matrimonio,
        'requiere_revision': matrimonio.requiere_revision,
    }

    pdf = generar_constancia_matrimonio(
        datos,
        observacion=observacion,
    )

    nombre_pareja = (
        f'{matrimonio.esposo or "matrimonio"}'
        f'_y_{matrimonio.esposa or "registro"}'
    )
    nombre_pareja = re.sub(
        r'[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ_-]+',
        '_',
        nombre_pareja,
    ).strip('_')

    nombre_archivo = (
        f'matrimonio_{numero_partida:03d}_{nombre_pareja}.pdf'
    )

    constancia = Constancia(
        tipo_sacramento='Matrimonio',
        numero_partida=numero_partida,
        id_registro=matrimonio.id,
        nombre_persona=(
            f'{matrimonio.esposo or ""} y '
            f'{matrimonio.esposa or ""}'
        ).strip(),
        usuario_emisor=request.session.get('username'),
        observaciones=observacion,
    )

    constancia.archivo_pdf.save(
        nombre_archivo,
        pdf,
        save=True,
    )

    try:
        ConstanciaEmitida.objects.using('historial').create(
            nombre=(
                f'{matrimonio.esposo or ""} y '
                f'{matrimonio.esposa or ""}'
            ).strip()[:200],
            sacramento='matrimonio',
            usuario=(
                request.session.get('username') or 'Desconocido'
            )[:150],
        )
    except Exception:
        pass

    return FileResponse(
        constancia.archivo_pdf.open('rb'),
        as_attachment=False,
        filename=nombre_archivo,
        content_type='application/pdf',
    )


@usuario_requerido
def listar_matrimonios(request):
    consulta = request.GET.get('q', '').strip()

    resultados = Matrimonio.objects.all()

    if consulta:
        resultados = resultados.filter(
            Q(esposo__icontains=consulta)
            | Q(esposa__icontains=consulta)
            | Q(libro__icontains=consulta)
        )

    resultados = resultados.order_by('-id')

    paginator = Paginator(resultados, 10)
    pagina = request.GET.get('pagina')
    page_obj = paginator.get_page(pagina)

    return render(
        request,
        'sacramentos/listar_matrimonios.html',
        {
            'page_obj': page_obj,
            'consulta': consulta,
            'total': paginator.count,
        }
    )


@usuario_requerido
def crear_matrimonio(request):
    if request.method == 'POST':
        formulario = MatrimonioForm(request.POST)

        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(
                    request,
                    'Registro de matrimonio creado correctamente.',
                )
                return redirect('listar_matrimonios')
            except Exception:
                messages.error(
                    request,
                    'No se pudo crear el registro de matrimonio.',
                )
        else:
            messages.error(
                request,
                'Revise los datos del formulario.',
            )
    else:
        formulario = MatrimonioForm()

    return render(
        request,
        'sacramentos/formulario_matrimonio.html',
        {
            'formulario': formulario,
            'accion': 'Crear',
        }
    )


@usuario_requerido
def ver_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)

    return render(
        request,
        'sacramentos/ver_matrimonio.html',
        {'registro': registro},
    )


@usuario_requerido
def editar_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)

    if request.method == 'POST':
        formulario = MatrimonioForm(
            request.POST,
            instance=registro,
        )

        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(
                    request,
                    'Registro de matrimonio actualizado correctamente.',
                )
                return redirect(
                    'ver_matrimonio',
                    pk=registro.pk,
                )
            except Exception:
                messages.error(
                    request,
                    'No se pudo actualizar el registro de matrimonio.',
                )
        else:
            messages.error(
                request,
                'Revise los datos del formulario.',
            )
    else:
        formulario = MatrimonioForm(instance=registro)

    return render(
        request,
        'sacramentos/formulario_matrimonio.html',
        {
            'formulario': formulario,
            'accion': 'Editar',
            'registro': registro,
        }
    )


@usuario_requerido
def eliminar_matrimonio(request, pk):
    registro = get_object_or_404(Matrimonio, pk=pk)

    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(
                request,
                'Registro de matrimonio eliminado correctamente.',
            )
            return redirect('listar_matrimonios')
        except Exception:
            messages.error(
                request,
                'No se pudo eliminar el registro de matrimonio.',
            )

    return render(
        request,
        'sacramentos/eliminar_matrimonio.html',
        {'registro': registro},
    )
