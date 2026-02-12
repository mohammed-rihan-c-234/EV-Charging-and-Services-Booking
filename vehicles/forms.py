from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["make", "model", "year", "license_plate"]
        widgets = {
            "make": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "license_plate": forms.TextInput(attrs={"class": "form-control"}),
        }

