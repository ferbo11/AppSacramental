from django.db import models


class Bautismo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_sacramentado = models.CharField(max_length=150)
    padre = models.CharField(max_length=150, blank=True, null=True)
    madre = models.CharField(max_length=150, blank=True, null=True)
    padrino_1 = models.CharField(max_length=150, blank=True, null=True)
    padrino_2 = models.CharField(max_length=150, blank=True, null=True)
    lugar_nacimiento = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    folio = models.IntegerField()
    libro = models.IntegerField()
    requiere_revision = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bautizos'

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
    def lugar_bautismo(self):
        return self.lugar_nacimiento

    @property
    def id_bautismo(self):
        return self.id

    def __str__(self):
        return self.nombre_sacramentado