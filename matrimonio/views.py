from django.shortcuts import render
from .models import Matrimonio


def buscar_matrimonio(request):

    esposo = request.GET.get('esposo', '').strip()
    esposa = request.GET.get('esposa', '').strip()

    resultados = Matrimonio.objects.all()

    if esposo:
        resultados = resultados.filter(
            nombre_esposo__icontains=esposo
        )

    if esposa:
        resultados = resultados.filter(
            nombre_esposa__icontains=esposa
        )

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