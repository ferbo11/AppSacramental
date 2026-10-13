from django.urls import path
from . import views

urlpatterns = [
    path('', views.configuracion_view, name='configuracion'),
]