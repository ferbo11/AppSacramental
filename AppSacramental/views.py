from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')


def index(request):
    return render(request, 'index.html')

def bautismo(request):
    return render(request, 'bautismo/bautismo.html')

def Hbautismo(request):
    return render(request, 'bautismo/historialBautismo.html')

def comunion(request):
    return render(request, 'comunion/comunion.html')

def Hcomunion(request):
    return render(request, 'comunion/historialComunion.html')

def confirmacion(request):
    return render(request, 'confirmacion/confirmacion.html')

def Hconfirmacion(request):
    return render(request, 'confirmacion/historialConfirmacion.html')

def matrimonio(request):
    return render(request, 'matrimonio/matrimonio.html')

def Hmatrimonio(request):  
    return render(request, 'matrimonio/historialMatrimonio.html')

def agenda(request):
    return render(request, 'agenda/agenda.html')    

def configuracion(request):
    return render(request, 'configuracion/configuracion.html')