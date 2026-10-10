from django.db import models


class Confirmacion(models.Model):
    id_confirmacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    nombre_padre = models.CharField(max_length=150, blank=True, null=True)
    nombre_madre = models.CharField(max_length=150, blank=True, null=True)
    nombre_padrino = models.CharField(max_length=150, blank=True, null=True)
    nombre_madrina = models.CharField(max_length=150, blank=True, null=True)
    folio = models.IntegerField()
    libro = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'confirmaciones'

    def __str__(self):
        return self.nombre