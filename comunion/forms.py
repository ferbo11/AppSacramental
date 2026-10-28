from django import forms

from .models import PrimeraComunion


class PrimeraComunionForm(forms.ModelForm):
    class Meta:
        model = PrimeraComunion
        fields = [
            'nombre_sacramentado',
            'padre',
            'madre',
            'bautizado_en',
            'fecha_sacramento',
            'folio',
            'libro',
            'requiere_revision',
        ]
        labels = {
            'nombre_sacramentado': 'Nombre del sacramentado',
            'padre': 'Padre',
            'madre': 'Madre',
            'bautizado_en': 'Bautizado en',
            'fecha_sacramento': 'Fecha del sacramento',
            'folio': 'Folio',
            'libro': 'Libro',
            'requiere_revision': 'Requiere revisión',
        }
        widgets = {
            'nombre_sacramentado': forms.TextInput(attrs={'class': 'form-control'}),
            'padre': forms.TextInput(attrs={'class': 'form-control'}),
            'madre': forms.TextInput(attrs={'class': 'form-control'}),
            'bautizado_en': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_sacramento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control'}),
            'libro': forms.NumberInput(attrs={'class': 'form-control'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
