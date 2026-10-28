from django import forms

from .models import Matrimonio


class MatrimonioForm(forms.ModelForm):
    class Meta:
        model = Matrimonio
        fields = [
            'esposo',
            'esposa',
            'libro',
            'folio',
            'ano',
            'mes',
            'dia',
            'fecha_matrimonio',
            'requiere_revision',
        ]
        labels = {
            'esposo': 'Esposo',
            'esposa': 'Esposa',
            'libro': 'Libro',
            'folio': 'Folio',
            'ano': 'Año',
            'mes': 'Mes',
            'dia': 'Día',
            'fecha_matrimonio': 'Fecha de matrimonio',
            'requiere_revision': 'Requiere revisión',
        }
        widgets = {
            'esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'libro': forms.TextInput(attrs={'class': 'form-control'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'mes': forms.TextInput(attrs={'class': 'form-control'}),
            'dia': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_matrimonio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
