from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)

from django.http import FileResponse

from .models import Confirmacion

from constancias.models import Constancia

from constancias.generador_confirmacion import (
    generar_constancia_confirmacion,
)

def buscar_confirmacion(request):

    nombre = request.GET.get(
        'nombre',
        ''
    ).strip()

    apellidos = request.GET.get(
        'apellidos',
        ''
    ).strip()

    resultados = Confirmacion.objects.all()

    if nombre:
        resultados = resultados.filter(
            nombre__icontains=nombre
        )

    if apellidos:
        resultados = resultados.filter(
            apellidos__icontains=apellidos
        )

    return render(
        request,
        'confirmacion/confirmacion.html',
        {
            'resultados': resultados,
            'nombre': nombre,
            'apellidos': apellidos,
            'busqueda_realizada': bool(
                nombre or apellidos
            ),
        }
    )


def generar_pdf_confirmacion(
    request,
    id_confirmacion
):

    if request.method != 'POST':

        return redirect(
            'confirmacion'
        )

    confirmacion = get_object_or_404(
        Confirmacion,
        id_confirmacion=id_confirmacion
    )

    observacion = request.POST.get(
        'observacion',
        ''
    ).strip()

    # ========================================================
    # OBTENER SIGUIENTE PARTIDA
    # ========================================================

    ultima_constancia = (
        Constancia.objects
        .filter(
            tipo_sacramento='Confirmación'
        )
        .order_by(
            '-numero_partida'
        )
        .first()
    )

    if ultima_constancia:

        numero_partida = (
            ultima_constancia.numero_partida
            + 1
        )

    else:

        numero_partida = 1

    # ========================================================
    # GENERAR PDF
    # ========================================================

    pdf = generar_constancia_confirmacion(
        confirmacion,
        numero_partida,
        observacion
    )

    # ========================================================
    # NOMBRE DEL ARCHIVO
    # ========================================================

    nombre_archivo = (
        f'confirmacion_'
        f'{numero_partida:03d}_'
        f'{confirmacion.nombre.replace(" ", "_")}.pdf'
    )

    # ========================================================
    # GUARDAR HISTORIAL
    # ========================================================

    constancia = Constancia(
        tipo_sacramento='Confirmación',
        numero_partida=numero_partida,
        id_registro=confirmacion.id_confirmacion,
        nombre_persona=confirmacion.nombre,
        usuario_emisor=request.session.get(
            'username'
        ),
        observaciones=(
            observacion
            or 'NINGUNA'
        )
    )

    constancia.archivo_pdf.save(
        nombre_archivo,
        pdf,
        save=True
    )

    # ========================================================
    # MOSTRAR PDF
    # ========================================================

    return FileResponse(
        constancia.archivo_pdf.open(
            'rb'
        ),
        as_attachment=False,
        filename=nombre_archivo,
        content_type='application/pdf'
    )