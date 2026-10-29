from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from AppSacramental.views import usuario_requerido

from .models import PrimeraComunion
from .forms import PrimeraComunionForm

from constancias.models import Constancia
from constancias.generador_comunion import generar_constancia_comunion

from historial.models import ConstanciaEmitida


# ============================================================
# BUSCAR PRIMERA COMUNIÓN
# ============================================================

def buscar_comunion(request):
    nombre = request.GET.get('nombre', '').strip()
    apellidos = request.GET.get('apellidos', '').strip()

    resultados = PrimeraComunion.objects.none()

    if nombre or apellidos:
        resultados = PrimeraComunion.objects.all()

        if nombre:
            resultados = resultados.filter(
                nombre_sacramentado__icontains=nombre
            )

        if apellidos:
            resultados = resultados.filter(
                nombre_sacramentado__icontains=apellidos
            )

    return render(
        request,
        'comunion/comunion.html',
        {
            'resultados': resultados,
            'nombre': nombre,
            'apellidos': apellidos,
            'busqueda_realizada': bool(nombre or apellidos),
        }
    )


# ============================================================
# GENERAR PDF DE PRIMERA COMUNIÓN
# ============================================================

def generar_pdf_comunion(request, id_comunion):

    if request.method != 'POST':
        return redirect('comunion')

    comunion = get_object_or_404(
        PrimeraComunion,
        pk=id_comunion
    )

    observacion = request.POST.get(
        'observacion',
        ''
    ).strip()

    if not observacion:
        observacion = 'NINGUNO'

    # --------------------------------------------------------
    # SIGUIENTE NÚMERO CONSECUTIVO DE CONSTANCIA
    # Este número no sustituye la partida del registro.
    # --------------------------------------------------------

    ultima_constancia = (
        Constancia.objects
        .filter(tipo_sacramento='Primera Comunión')
        .order_by('-numero_partida')
        .first()
    )

    if ultima_constancia:
        numero_partida = ultima_constancia.numero_partida + 1
    else:
        numero_partida = 1

    # --------------------------------------------------------
    # GENERAR PDF
    # --------------------------------------------------------

    pdf = generar_constancia_comunion(
        comunion,
        numero_partida,
        observacion
    )

    # --------------------------------------------------------
    # NOMBRE DEL ARCHIVO
    # --------------------------------------------------------

    nombre_archivo = (
        f'primera_comunion_'
        f'{numero_partida:03d}_'
        f'{comunion.nombre.replace(" ", "_")}.pdf'
    )

    # --------------------------------------------------------
    # GUARDAR CONSTANCIA
    # --------------------------------------------------------

    constancia = Constancia(
        tipo_sacramento='Primera Comunión',
        numero_partida=numero_partida,
        id_registro=comunion.id_comunion,
        nombre_persona=comunion.nombre,
        usuario_emisor=request.session.get('username'),
        observaciones=observacion
    )

    constancia.archivo_pdf.save(
        nombre_archivo,
        pdf,
        save=True
    )

    # --------------------------------------------------------
    # REGISTRAR EN EL HISTORIAL
    # --------------------------------------------------------

    ConstanciaEmitida.objects.using('historial').create(
        nombre=comunion.nombre[:200],
        sacramento='comunion',
        usuario=(
            request.session.get('username')
            or 'Desconocido'
        )[:150],
    )

    # --------------------------------------------------------
    # MOSTRAR PDF
    # --------------------------------------------------------

    return FileResponse(
        constancia.archivo_pdf.open('rb'),
        as_attachment=False,
        filename=nombre_archivo,
        content_type='application/pdf'
    )
       # ========================================================
    # REGISTRAR EN EL HISTORIAL (SQLite)
    # ========================================================

    ConstanciaEmitida.objects.using('historial').create(
        nombre=comunion.nombre[:200],
        sacramento='comunion',
        usuario=(
            request.session.get('username')
            or 'Desconocido'
        )[:150],
        id_constancia=constancia.id_constancia,
    )

# ============================================================
# LISTAR PRIMERAS COMUNIONES
# ============================================================

@usuario_requerido
def listar_comuniones(request):
    consulta = request.GET.get('q', '').strip()

    resultados = PrimeraComunion.objects.all()

    if consulta:
        resultados = resultados.filter(
            Q(nombre_sacramentado__icontains=consulta)
            | Q(padre__icontains=consulta)
            | Q(madre__icontains=consulta)
            | Q(bautizado_en__icontains=consulta)
        )

    resultados = resultados.order_by('-id')

    paginator = Paginator(resultados, 10)
    pagina = request.GET.get('pagina')
    page_obj = paginator.get_page(pagina)

    return render(
        request,
        'sacramentos/listar_comuniones.html',
        {
            'page_obj': page_obj,
            'consulta': consulta,
            'total': paginator.count,
        }
    )


# ============================================================
# CREAR PRIMERA COMUNIÓN
# ============================================================

@usuario_requerido
def crear_comunion(request):

    if request.method == 'POST':
        formulario = PrimeraComunionForm(request.POST)

        if formulario.is_valid():
            try:
                formulario.save()

                messages.success(
                    request,
                    'Registro de primera comunión creado correctamente.'
                )

                return redirect('listar_comuniones')

            except Exception:
                messages.error(
                    request,
                    'No se pudo crear el registro de primera comunión.'
                )
        else:
            messages.error(
                request,
                'Revise los datos del formulario.'
            )

    else:
        formulario = PrimeraComunionForm()

    return render(
        request,
        'sacramentos/formulario_comunion.html',
        {
            'formulario': formulario,
            'accion': 'Crear',
        }
    )


# ============================================================
# VER PRIMERA COMUNIÓN
# ============================================================

@usuario_requerido
def ver_comunion(request, pk):
    registro = get_object_or_404(
        PrimeraComunion,
        pk=pk
    )

    return render(
        request,
        'sacramentos/ver_comunion.html',
        {'registro': registro}
    )


# ============================================================
# EDITAR PRIMERA COMUNIÓN
# ============================================================

@usuario_requerido
def editar_comunion(request, pk):

    registro = get_object_or_404(
        PrimeraComunion,
        pk=pk
    )

    if request.method == 'POST':
        formulario = PrimeraComunionForm(
            request.POST,
            instance=registro
        )

        if formulario.is_valid():
            try:
                formulario.save()

                messages.success(
                    request,
                    'Registro de primera comunión actualizado correctamente.'
                )

                return redirect(
                    'ver_comunion',
                    pk=registro.pk
                )

            except Exception:
                messages.error(
                    request,
                    'No se pudo actualizar el registro de primera comunión.'
                )

        else:
            messages.error(
                request,
                'Revise los datos del formulario.'
            )

    else:
        formulario = PrimeraComunionForm(
            instance=registro
        )

    return render(
        request,
        'sacramentos/formulario_comunion.html',
        {
            'formulario': formulario,
            'accion': 'Editar',
            'registro': registro,
        }
    )


# ============================================================
# ELIMINAR PRIMERA COMUNIÓN
# ============================================================

@usuario_requerido
def eliminar_comunion(request, pk):

    registro = get_object_or_404(
        PrimeraComunion,
        pk=pk
    )

    if request.method == 'POST':
        try:
            registro.delete()

            messages.success(
                request,
                'Registro de primera comunión eliminado correctamente.'
            )

            return redirect('listar_comuniones')

        except Exception:
            messages.error(
                request,
                'No se pudo eliminar el registro de primera comunión.'
            )

    return render(
        request,
        'sacramentos/eliminar_comunion.html',
        {'registro': registro}
    )