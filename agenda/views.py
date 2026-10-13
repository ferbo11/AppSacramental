import json

from datetime import date

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import IntegrityError, transaction

from .models import Actividad


@require_GET
def actividades_api(request):
    actividades = Actividad.objects.using("agenda").order_by(
        "fecha", "hora"
    )

    datos = [
        {
            "id": actividad.pk,
            "fecha": actividad.fecha.isoformat(),
            "hora": actividad.hora.strftime("%H:%M"),
            "sacramento": actividad.sacramento,
            "nombre": actividad.nombre,
            "observaciones": actividad.observaciones,
        }
        for actividad in actividades
    ]

    return JsonResponse({"actividades": datos})


@require_POST
def crear_actividad(request):
    try:
        fecha = date.fromisoformat(request.POST.get("fecha", ""))
        hora = request.POST.get("hora", "").strip()
        sacramento = request.POST.get("sacramento", "").strip()
        nombre = request.POST.get("nombre", "").strip()
        observaciones = request.POST.get("observaciones", "").strip()

        if not hora or not sacramento or not nombre:
            return JsonResponse(
                {"error": "Completa todos los campos obligatorios."},
                status=400,
            )

        if sacramento not in {
            "Bautismo",
            "Primera Comunión",
            "Confirmación",
            "Matrimonio",
            "Otro",
        }:
            return JsonResponse(
                {"error": "El sacramento seleccionado no es válido."},
                status=400,
            )

        from datetime import time

        hora_validada = time.fromisoformat(hora)

        if fecha < date.today():
            return JsonResponse(
                {"error": "No puedes apartar una fecha pasada."},
                status=400,
            )

        with transaction.atomic(using="agenda"):
            ocupada = Actividad.objects.using("agenda").filter(
                fecha=fecha,
                hora=hora_validada,
            ).exists()

            if ocupada:
                return JsonResponse(
                    {
                        "error": (
                            "Ya existe una actividad programada "
                            "para esa fecha y hora."
                        )
                    },
                    status=409,
                )

            actividad = Actividad.objects.using("agenda").create(
                fecha=fecha,
                hora=hora_validada,
                sacramento=sacramento,
                nombre=nombre,
                observaciones=observaciones,
            )

        return JsonResponse(
            {
                "mensaje": "Actividad registrada correctamente.",
                "actividad": {
                    "id": actividad.pk,
                    "fecha": actividad.fecha.isoformat(),
                    "hora": actividad.hora.strftime("%H:%M"),
                    "sacramento": actividad.sacramento,
                    "nombre": actividad.nombre,
                    "observaciones": actividad.observaciones,
                },
            },
            status=201,
        )

    except ValueError:
        return JsonResponse(
            {"error": "La fecha o la hora no tienen un formato válido."},
            status=400,
        )

    except IntegrityError:
        return JsonResponse(
            {"error": "No se pudo registrar la actividad."},
            status=400,
        )