from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def bautismo(request):
    return render(request, 'bautismo/bautismo.html')

def comunion(request):
    return render(request, 'comunion/comunion.html')

def confirmacion(request):
    return render(request, 'confirmacion/confirmacion.html')

def matrimonio(request):
    return render(request, 'matrimonio/matrimonio.html')