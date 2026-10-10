from functools import wraps
from django.shortcuts import redirect, render


def usuario_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('/login/')
        return view_func(request, *args, **kwargs)

    return wrapper
    
@usuario_requerido
def index(request):
    return render(request, 'index.html')

@usuario_requerido
def bautismo(request):
    return render(request, 'bautismo/bautismo.html')

@usuario_requerido
def Hbautismo(request):
    return render(request, 'bautismo/historialBautismo.html')

@usuario_requerido
def comunion(request):
    return render(request, 'comunion/comunion.html')

@usuario_requerido
def Hcomunion(request):
    return render(request, 'comunion/historialComunion.html')

@usuario_requerido
def confirmacion(request):
    return render(request, 'confirmacion/confirmacion.html')

@usuario_requerido
def Hconfirmacion(request):
    return render(request, 'confirmacion/historialConfirmacion.html')

@usuario_requerido
def matrimonio(request):
    return render(request, 'matrimonio/matrimonio.html')

@usuario_requerido
def Hmatrimonio(request):  
    return render(request, 'matrimonio/historialMatrimonio.html')

@usuario_requerido
def agenda(request):
    return render(request, 'agenda/agenda.html')    

@usuario_requerido
def configuracion(request):
    return render(request, 'configuracion/configuracion.html')