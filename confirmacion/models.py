from django.db import models


class Confirmacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_sacramentado = models.CharField(max_length=150)
    padre = models.CharField(max_length=150, blank=True, null=True)
    madre = models.CharField(max_length=150, blank=True, null=True)
    padrino_1 = models.CharField(max_length=150, blank=True, null=True)
    padrino_2 = models.CharField(max_length=150, blank=True, null=True)
    fecha_sacramento = models.DateField()
    folio = models.IntegerField()
    libro = models.IntegerField()
    partida = models.IntegerField()
    requiere_revision = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'confirmaciones'

    @property
    def nombre(self):
        return self.nombre_sacramentado

    @property
    def nombre_padre(self):
        return self.padre

    @property
    def nombre_madre(self):
        return self.madre

    @property
    def nombre_padrino(self):
        return self.padrino_1

    @property
    def nombre_madrina(self):
        return self.padrino_2

    @property
    def fecha(self):
        return self.fecha_sacramento

    @property
    def id_confirmacion(self):
        return self.id

    @property
    def creado_en(self):
        return None

    def __str__(self):
        return self.nombre_sacramentado