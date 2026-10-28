from django.db import models


class Matrimonio(models.Model):
    id = models.AutoField(primary_key=True)
    esposo = models.CharField(max_length=150, blank=True, null=True)
    esposa = models.CharField(max_length=150, blank=True, null=True)
    libro = models.CharField(max_length=50, blank=True, null=True)
    folio = models.IntegerField(blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    mes = models.CharField(max_length=20, blank=True, null=True)
    dia = models.IntegerField(blank=True, null=True)
    fecha_matrimonio = models.DateField(blank=True, null=True)
    requiere_revision = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'matrimonios'

    @property
    def nombre_esposo(self):
        return self.esposo

    @property
    def nombre_esposa(self):
        return self.esposa

    @property
    def anio(self):
        return self.ano

    @property
    def id_matrimonio(self):
        return self.id

    @property
    def creado_en(self):
        return None

    def __str__(self):
        return f"{self.esposo or ''} y {self.esposa or ''}".strip()