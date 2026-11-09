from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.index,
        name='backups_index',
    ),
    path(
        'crear/',
        views.crear,
        name='backups_crear',
    ),
    path(
        'descargar/<str:nombre>/',
        views.descargar,
        name='backups_descargar',
    ),
    path(
        'eliminar/',
        views.eliminar,
        name='backups_eliminar',
    ),
    path(
        'restaurar/',
        views.restaurar,
        name='backups_restaurar',
    ),
]
