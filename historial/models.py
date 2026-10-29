from django.db import models


class ConstanciaEmitida(models.Model):

    SACRAMENTOS = [
        ('bautismo', 'Bautismo'),
        ('comunion', 'Primera Comunión'),
        ('confirmacion', 'Confirmación'),
        ('matrimonio', 'Matrimonio'),
    ]

    nombre = models.CharField(max_length=200)

    sacramento = models.CharField(
        max_length=30,
        choices=SACRAMENTOS,
        db_index=True,
    )

    usuario = models.CharField(
        max_length=150,
        db_index=True,
    )

    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    id_constancia = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Constancia emitida'
        verbose_name_plural = 'Constancias emitidas'

    def __str__(self):
        return (
            f'{self.get_sacramento_display()} - '
            f'{self.nombre}'
        )