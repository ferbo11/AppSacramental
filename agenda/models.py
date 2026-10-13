from django.db import models


class Actividad(models.Model):

    SACRAMENTOS = [
        ("Bautismo", "Bautismo"),
        ("Primera Comunión", "Primera Comunión"),
        ("Confirmación", "Confirmación"),
        ("Matrimonio", "Matrimonio"),
        ("Otro", "Otro"),
    ]

    fecha = models.DateField()

    hora = models.TimeField()

    sacramento = models.CharField(
        max_length=30,
        choices=SACRAMENTOS
    )

    nombre = models.CharField(
        max_length=150
    )

    observaciones = models.TextField(
        blank=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["fecha", "hora"]

    def __str__(self):
        return f"{self.sacramento} - {self.fecha} {self.hora}"