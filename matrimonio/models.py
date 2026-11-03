from django.db import models


class Matrimonio(models.Model):
    id = models.AutoField(primary_key=True)

    esposo = models.CharField(max_length=150, blank=True, null=True)
    edad_esposo = models.IntegerField(blank=True, null=True)

    esposa = models.CharField(max_length=150, blank=True, null=True)
    edad_esposa = models.IntegerField(blank=True, null=True)

    padre_esposo = models.CharField(max_length=150, blank=True, null=True)
    madre_esposo = models.CharField(max_length=150, blank=True, null=True)
    padre_esposa = models.CharField(max_length=150, blank=True, null=True)
    madre_esposa = models.CharField(max_length=150, blank=True, null=True)

    testigo_1 = models.CharField(max_length=150, blank=True, null=True)
    testigo_2 = models.CharField(max_length=150, blank=True, null=True)

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

    @property
    def testigos(self):
        return ' y '.join(
            testigo.strip()
            for testigo in (self.testigo_1, self.testigo_2)
            if testigo and testigo.strip()
        )

    @property
    def datos_faltantes(self):
        faltantes = []

        if not self.esposo or not str(self.esposo).strip():
            faltantes.append('Nombre del esposo')

        if not self.esposa or not str(self.esposa).strip():
            faltantes.append('Nombre de la esposa')

        if not self.libro or not str(self.libro).strip():
            faltantes.append('Libro')

        if self.folio is None:
            faltantes.append('Folio')

        if (
            self.fecha_matrimonio is None
            and self.ano is None
            and not self.mes
            and self.dia is None
        ):
            faltantes.append('Fecha del matrimonio')

        return faltantes

    def __str__(self):
        return f"{self.esposo or ''} y {self.esposa or ''}".strip()
