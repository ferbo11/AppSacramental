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

from bautismo.views import (
    buscar_bautismo,
    generar_pdf_bautismo,
    listar_bautismos,
    crear_bautismo,
    ver_bautismo,
    editar_bautismo,
    eliminar_bautismo,
)

from comunion.views import (
    buscar_comunion,
    generar_pdf_comunion,
    listar_comuniones,
    crear_comunion,
    ver_comunion,
    editar_comunion,
    eliminar_comunion,
)

from confirmacion.views import (
    buscar_confirmacion,
    generar_pdf_confirmacion,
    listar_confirmaciones,
    crear_confirmacion,
    ver_confirmacion,
    editar_confirmacion,
    eliminar_confirmacion,
)

from matrimonio.views import (
    buscar_matrimonio,
    generar_pdf_matrimonio,
    listar_matrimonios,
    crear_matrimonio,
    ver_matrimonio,
    editar_matrimonio,
    eliminar_matrimonio,
)

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
        "bautismo/generar-pdf/<int:id_bautismo>/",
        generar_pdf_bautismo,
        name="generar_pdf_bautismo",
    ),
    path(
        "bautismo/historial/",
        Hbautismo,
        name="historial_bautismo",
    ),
    path("sacramentos/bautismo/", listar_bautismos, name="listar_bautismos"),
    path("sacramentos/bautismo/crear/", crear_bautismo, name="crear_bautismo"),
    path("sacramentos/bautismo/<int:pk>/", ver_bautismo, name="ver_bautismo"),
    path("sacramentos/bautismo/<int:pk>/editar/", editar_bautismo, name="editar_bautismo"),
    path("sacramentos/bautismo/<int:pk>/eliminar/", eliminar_bautismo, name="eliminar_bautismo"),

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
    path("sacramentos/comunion/", listar_comuniones, name="listar_comuniones"),
    path("sacramentos/comunion/crear/", crear_comunion, name="crear_comunion"),
    path("sacramentos/comunion/<int:pk>/", ver_comunion, name="ver_comunion"),
    path("sacramentos/comunion/<int:pk>/editar/", editar_comunion, name="editar_comunion"),
    path("sacramentos/comunion/<int:pk>/eliminar/", eliminar_comunion, name="eliminar_comunion"),

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
    path("sacramentos/confirmacion/", listar_confirmaciones, name="listar_confirmaciones"),
    path("sacramentos/confirmacion/crear/", crear_confirmacion, name="crear_confirmacion"),
    path("sacramentos/confirmacion/<int:pk>/", ver_confirmacion, name="ver_confirmacion"),
    path("sacramentos/confirmacion/<int:pk>/editar/", editar_confirmacion, name="editar_confirmacion"),
    path("sacramentos/confirmacion/<int:pk>/eliminar/", eliminar_confirmacion, name="eliminar_confirmacion"),

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
        "matrimonio/generar-pdf/<int:id_matrimonio>/",
        generar_pdf_matrimonio,
        name="generar_pdf_matrimonio",
    ),
    path(
        "matrimonio/historial/",
        Hmatrimonio,
        name="historial_matrimonio",
    ),
    path("sacramentos/matrimonio/", listar_matrimonios, name="listar_matrimonios"),
    path("sacramentos/matrimonio/crear/", crear_matrimonio, name="crear_matrimonio"),
    path("sacramentos/matrimonio/<int:pk>/", ver_matrimonio, name="ver_matrimonio"),
    path("sacramentos/matrimonio/<int:pk>/editar/", editar_matrimonio, name="editar_matrimonio"),
    path("sacramentos/matrimonio/<int:pk>/eliminar/", eliminar_matrimonio, name="eliminar_matrimonio"),

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
        include("configuracion.urls"),
    ),
]


# Archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )