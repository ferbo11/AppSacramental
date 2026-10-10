"""
URL configuration for AppSacramental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    index,
    bautismo,
    Hbautismo,
    comunion,
    Hcomunion,
    confirmacion,
    Hconfirmacion,
    matrimonio,
    Hmatrimonio,
    agenda,
    configuracion,
)
from bautismo.views import buscar_bautismo
from comunion.views import (
    buscar_comunion,
    generar_pdf_comunion,
)
from confirmacion.views import (
    buscar_confirmacion,
    generar_pdf_confirmacion,
)
from matrimonio.views import buscar_matrimonio

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('bautismo/', bautismo, name='bautismo'),
    path('bautismo/buscar/', buscar_bautismo, name='buscar_bautismo'),
    path('bautismo/historial/', Hbautismo, name='historial_bautismo'),
    path('comunion/', comunion, name='comunion'),   
    path('comunion/buscar/', buscar_comunion, name='buscar_comunion'), 
    path('comunion/generar_pdf/<int:id_comunion>/', generar_pdf_comunion, name='generar_pdf_comunion'),
    path('comunion/historial/', Hcomunion, name='historial_comunion'),
    path('confirmacion/', confirmacion, name='confirmacion'),
    path('confirmacion/buscar/', buscar_confirmacion, name='buscar_confirmacion'),
    path('confirmacion/generar_pdf/<int:id_confirmacion>/', generar_pdf_confirmacion, name='generar_pdf_confirmacion'),
    path('confirmacion/historial/', Hconfirmacion, name='historial_confirmacion'),
    path('matrimonio/', matrimonio, name='matrimonio'),
    path('matrimonio/buscar/', buscar_matrimonio, name='buscar_matrimonio'),
    path('matrimonio/historial/', Hmatrimonio, name='historial_matrimonio'),
    path('login/', include('usuarios.urls')),
    path('agenda/', agenda, name='agenda'),
    path('configuracion/', configuracion, name='configuracion')  
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)