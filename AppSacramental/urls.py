"""
Configuración de URLs del proyecto AppSacramental.
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

from agenda.views import (
    actividades_api,
    crear_actividad,
)


urlpatterns = [
    # Administración de Django
    path(
        "admin/",
        admin.site.urls,
    ),

    # Autenticación
    path(
        "login/",
        include("usuarios.urls"),
    ),

    # Inicio / Dashboard
    path(
        "",
        index,
        name="index",
    ),

    # Bautismo
    path(
        "bautismo/",
        bautismo,
        name="bautismo",
    ),
    path(
        "bautismo/buscar/",
        buscar_bautismo,
        name="buscar_bautismo",
    ),
    path(
        "bautismo/historial/",
        Hbautismo,
        name="historial_bautismo",
    ),

    # Primera Comunión
    path(
        "comunion/",
        comunion,
        name="comunion",
    ),
    path(
        "comunion/buscar/",
        buscar_comunion,
        name="buscar_comunion",
    ),
    path(
        "comunion/generar-pdf/<int:id_comunion>/",
        generar_pdf_comunion,
        name="generar_pdf_comunion",
    ),
    path(
        "comunion/historial/",
        Hcomunion,
        name="historial_comunion",
    ),

    # Confirmación
    path(
        "confirmacion/",
        confirmacion,
        name="confirmacion",
    ),
    path(
        "confirmacion/buscar/",
        buscar_confirmacion,
        name="buscar_confirmacion",
    ),
    path(
        "confirmacion/generar-pdf/<int:id_confirmacion>/",
        generar_pdf_confirmacion,
        name="generar_pdf_confirmacion",
    ),
    path(
        "confirmacion/historial/",
        Hconfirmacion,
        name="historial_confirmacion",
    ),

    # Matrimonio
    path(
        "matrimonio/",
        matrimonio,
        name="matrimonio",
    ),
    path(
        "matrimonio/buscar/",
        buscar_matrimonio,
        name="buscar_matrimonio",
    ),
    path(
        "matrimonio/historial/",
        Hmatrimonio,
        name="historial_matrimonio",
    ),

    # Agenda parroquial
    path(
        "agenda/",
        agenda,
        name="agenda",
    ),
    path(
        "agenda/actividades/",
        actividades_api,
        name="agenda_actividades",
    ),
    path(
        "agenda/crear/",
        crear_actividad,
        name="crear_actividad",
    ),

    # Configuración
    path(
        "configuracion/",
        configuracion,
        name="configuracion",
    ),
]


# Archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )