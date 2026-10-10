from django.db import models


class Constancia(models.Model):

    SACRAMENTO_CHOICES = [
        ('Bautismo', 'Bautismo'),
        ('Primera Comunión', 'Primera Comunión'),
        ('Confirmación', 'Confirmación'),
        ('Matrimonio', 'Matrimonio'),
    ]

    id_constancia = models.AutoField(
        primary_key=True
    )

    tipo_sacramento = models.CharField(
        max_length=50,
        choices=SACRAMENTO_CHOICES
    )

    numero_partida = models.IntegerField(
        default=0
    )

    id_registro = models.IntegerField()

    nombre_persona = models.CharField(
        max_length=300
    )

    fecha_emision = models.DateTimeField(
        auto_now_add=True
    )

    usuario_emisor = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    archivo_pdf = models.FileField(
        upload_to='constancias/%Y/%m/'
    )

    class Meta:
        db_table = 'constancias'
        ordering = ['-fecha_emision']

    def __str__(self):
        return (
            f'{self.tipo_sacramento} '
            f'- Partida {self.numero_partida} '
            f'- {self.nombre_persona}'
        )