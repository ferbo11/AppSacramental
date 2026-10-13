from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse

from .models import PrimeraComunion

from constancias.models import Constancia

from constancias.generador_comunion import (
    generar_constancia_comunion
)

from historial.models import ConstanciaEmitida


def buscar_comunion(request):
    nombre = request.GET.get('nombre', '').strip()
    apellidos = request.GET.get('apellidos', '').strip()

    resultados = PrimeraComunion.objects.all()

    if nombre:
        resultados = resultados.filter(nombre__icontains=nombre)

    if apellidos:
        resultados = resultados.filter(nombre__icontains=apellidos)

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
        id_comunion=id_comunion
    )

    # ========================================================
    # OBSERVACIÓN
    # ========================================================

    observacion = request.POST.get(
        'observacion',
        ''
    ).strip()

    if not observacion:
        observacion = 'NINGUNO'

    # ========================================================
    # SIGUIENTE PARTIDA
    # ========================================================

    ultima_constancia = (
        Constancia.objects
        .filter(
            tipo_sacramento='Primera Comunión'
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

    # ========================================================
    # GENERAR PDF
    # ========================================================

    pdf = generar_constancia_comunion(
        comunion,
        numero_partida,
        observacion
    )

    # ========================================================
    # NOMBRE DEL ARCHIVO
    # ========================================================

    nombre_archivo = (
        f'primera_comunion_'
        f'{numero_partida:03d}_'
        f'{comunion.nombre.replace(" ", "_")}.pdf'
    )

    # ========================================================
    # GUARDAR HISTORIAL
    # ========================================================

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
    )

    # ========================================================
    # MOSTRAR PDF
    # ========================================================

    return FileResponse(
        constancia.archivo_pdf.open('rb'),
        as_attachment=False,
        filename=nombre_archivo,
        content_type='application/pdf'
    )