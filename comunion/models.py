from django.db import models


class PrimeraComunion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_sacramentado = models.CharField(max_length=150)
    padre = models.CharField(max_length=150, blank=True, null=True)
    madre = models.CharField(max_length=150, blank=True, null=True)
    bautizado_en = models.CharField(max_length=150, blank=True, null=True)
    fecha_sacramento = models.DateField(blank=True, null=True)
    folio = models.IntegerField()
    libro = models.IntegerField()
    requiere_revision = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'primera_comunion'

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
        return None

    @property
    def nombre_madrina(self):
        return None

    @property
    def id_comunion(self):
        return self.id

    @property
    def creado_en(self):
        return None

    def __str__(self):
        return self.nombre_sacramentado