from django.db import models


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(
        unique=True,
        max_length=50
    )

    class Meta:
        managed = False
        db_table = 'roles'

    def __str__(self):
        return self.nombre_rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(
        unique=True,
        max_length=50
    )
    password_hash = models.CharField(max_length=255)

    id_rol = models.ForeignKey(
        Rol,
        models.DO_NOTHING,
        db_column='id_rol',
        blank=True,
        null=True
    )

    creado_en = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'usuarios'

    def __str__(self):
        return self.username