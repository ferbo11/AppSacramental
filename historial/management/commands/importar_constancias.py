from django.core.management.base import BaseCommand
from django.db import transaction

from constancias.models import Constancia
from historial.models import ConstanciaEmitida


MAPA_SACRAMENTOS = {
    'Bautismo': 'bautismo',
    'Primera Comunión': 'comunion',
    'Confirmación': 'confirmacion',
    'Matrimonio': 'matrimonio',
}


def normalizar_tipo(tipo):
    return MAPA_SACRAMENTOS.get((tipo or '').strip())


def construir_registro(constancia):
    codigo = normalizar_tipo(constancia.tipo_sacramento)

    if codigo is None:
        return None

    return {
        'nombre': (constancia.nombre_persona or '')[:200],
        'sacramento': codigo,
        'usuario': (constancia.usuario_emisor or 'Desconocido')[:150],
        'fecha_emision': constancia.fecha_emision,
    }


class Command(BaseCommand):
    help = (
        'Importa las constancias historicas de PostgreSQL a la base '
        'historial (SQLite). Por defecto solo simula; use --ejecutar '
        'para escribir.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--ejecutar',
            action='store_true',
            help='Realiza la importacion. Sin esta opcion solo simula.',
        )

    def handle(self, *args, **opciones):
        ejecutar = opciones['ejecutar']

        origen = (
            Constancia.objects.using('default')
            .order_by('fecha_emision')
        )

        total = origen.count()

        self.stdout.write(
            f'Constancias encontradas en PostgreSQL: {total}'
        )

        registros = []
        ignoradas = 0

        for constancia in origen:
            registro = construir_registro(constancia)

            if registro is None:
                ignoradas += 1
                continue

            registros.append(registro)

        self.stdout.write(
            f'Registros a importar: {len(registros)}'
        )

        self.stdout.write(
            'Registros ignorados por tipo desconocido: '
            f'{ignoradas}'
        )

        destino = ConstanciaEmitida.objects.using('historial')

        existentes = set(
            destino.values_list(
                'sacramento',
                'nombre',
                'fecha_emision',
            )
        )

        nuevos = [
            registro
            for registro in registros
            if (
                registro['sacramento'],
                registro['nombre'],
                registro['fecha_emision'],
            ) not in existentes
        ]

        self.stdout.write(
            f'Registros nuevos (sin duplicados): {len(nuevos)}'
        )

        if not ejecutar:
            self.stdout.write(
                self.style.WARNING(
                    'SIMULACION: no se escribio ningun registro.'
                )
            )
            self.stdout.write(
                'Ejecute de nuevo con --ejecutar para importar.'
            )
            return

        with transaction.atomic(using='historial'):
            for registro in nuevos:
                fecha = registro.pop('fecha_emision')

                creado = (
                    ConstanciaEmitida.objects.using('historial')
                    .create(**registro)
                )

                destino.filter(pk=creado.pk).update(
                    fecha_emision=fecha
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Importacion completada: {len(nuevos)} registros.'
            )
        )
