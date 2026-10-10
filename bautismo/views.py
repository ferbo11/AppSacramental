from django.shortcuts import render
from .models import Bautismo


def buscar_bautismo(request):
    nombre = request.GET.get('nombre', '').strip()
    apellidos = request.GET.get('apellidos', '').strip()

    resultados = Bautismo.objects.all()

    if nombre:
        resultados = resultados.filter(nombre__icontains=nombre)

    if apellidos:
        resultados = resultados.filter(nombre__icontains=apellidos)

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