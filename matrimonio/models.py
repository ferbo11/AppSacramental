from django.db import models


class Matrimonio(models.Model):
    id_matrimonio = models.AutoField(primary_key=True)
    nombre_esposo = models.CharField(max_length=150)
    nombre_esposa = models.CharField(max_length=150, blank=True, null=True)
    libro = models.IntegerField()
    folio = models.IntegerField()
    anio = models.IntegerField()
    creado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'matrimonios'

    def __str__(self):
        return f"{self.nombre_esposo} y {self.nombre_esposa or ''}".strip()