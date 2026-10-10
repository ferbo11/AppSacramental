from django.db import models


class Bautismo(models.Model):
    id_bautismo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    nombre_padre = models.CharField(max_length=150, blank=True, null=True)
    nombre_madre = models.CharField(max_length=150, blank=True, null=True)
    libro = models.IntegerField()
    folio = models.IntegerField()
    fecha = models.DateField()
    lugar_bautismo = models.CharField(max_length=150, blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bautismos'

    def __str__(self):
        return self.nombre