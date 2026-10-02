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
from .views import index, bautismo, comunion, confirmacion, matrimonio, Hbautismo, Hcomunion, Hconfirmacion, Hmatrimonio, agenda, configuracion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('bautismo/', bautismo, name='bautismo'),
    path('bautismo/historial/', Hbautismo, name='historial_bautismo'),
    path('comunion/', comunion, name='comunion'),    
    path('comunion/historial/', Hcomunion, name='historial_comunion'),
    path('confirmacion/', confirmacion, name='confirmacion'),
    path('confirmacion/historial/', Hconfirmacion, name='historial_confirmacion'),
    path('matrimonio/', matrimonio, name='matrimonio'),
    path('matrimonio/historial/', Hmatrimonio, name='historial_matrimonio'),
    path('login/', include('usuarios.urls')),
    path('agenda/', agenda, name='agenda'),
    path('configuracion/', configuracion, name='configuracion')  
]
