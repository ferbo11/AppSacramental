from functools import wraps
from django.shortcuts import redirect, render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from historial.models import ConstanciaEmitida

def usuario_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('/login/')
        return view_func(request, *args, **kwargs)

    return wrapper
    
@usuario_requerido
def index(request):
    # Consultar exclusivamente el historial en historial.sqlite3
    historial = ConstanciaEmitida.objects.using('historial')

    # 1. Cantidad de constancias por sacramento
    conteo_sacramentos = (
        historial.values('sacramento')
        .annotate(total=Count('id'))
    )

    conteo_por_sacramento = {
        item['sacramento']: item['total']
        for item in conteo_sacramentos
    }

    sacramentos = [
        {
            'codigo': 'bautismo',
            'nombre': 'Bautismo',
        },
        {
            'codigo': 'comunion',
            'nombre': 'Primera Comunión',
        },
        {
            'codigo': 'confirmacion',
            'nombre': 'Confirmación',
        },
        {
            'codigo': 'matrimonio',
            'nombre': 'Matrimonio',
        },
    ]

    etiquetas_sacramentos = [
        sacramento['nombre']
        for sacramento in sacramentos
    ]

    datos_sacramentos = [
        conteo_por_sacramento.get(sacramento['codigo'], 0)
        for sacramento in sacramentos
    ]

    # 2. Emisiones por mes del año actual
    anio_actual = timezone.localdate().year

    emisiones_mensuales = (
        historial.filter(fecha_emision__year=anio_actual)
        .annotate(mes=TruncMonth('fecha_emision'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    conteo_meses = {
        registro['mes'].month: registro['total']
        for registro in emisiones_mensuales
        if registro['mes'] is not None
    }

    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril',
        'Mayo', 'Junio', 'Julio', 'Agosto',
        'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
    ]

    etiquetas_meses = nombres_meses

    datos_meses = [
        conteo_meses.get(numero_mes, 0)
        for numero_mes in range(1, 13)
    ]

    # 3. Historial reciente para la tabla del dashboard
    historial_reciente = historial.all()[:10]

    # 4. Total general de constancias emitidas
    total_constancias = historial.count()

    contexto = {
        'total_constancias': total_constancias,
        'historial_constancias': historial_reciente,

        'etiquetas_sacramentos': etiquetas_sacramentos,
        'datos_sacramentos': datos_sacramentos,

        'etiquetas_meses': etiquetas_meses,
        'datos_meses': datos_meses,

        'anio_actual': anio_actual,
    }

    return render(request, 'index.html', contexto)

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