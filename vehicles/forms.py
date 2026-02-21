from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("make", "model", "year", "license_plate"):
            self.fields[name].required = True
            self.fields[name].widget.attrs["required"] = "required"

    def clean_make(self):
        value = (self.cleaned_data.get("make") or "").strip()
        if not value:
            raise forms.ValidationError("Make is required.")
        return value

    def clean_model(self):
        value = (self.cleaned_data.get("model") or "").strip()
        if not value:
            raise forms.ValidationError("Model is required.")
        return value

    def clean_license_plate(self):
        value = (self.cleaned_data.get("license_plate") or "").strip()
        if not value:
            raise forms.ValidationError("License plate is required.")
        return value

    def clean_year(self):
        value = self.cleaned_data.get("year")
        if value in (None, ""):
            raise forms.ValidationError("Year is required.")
        return value

    class Meta:
        model = Vehicle
        fields = ["make", "model", "year", "license_plate"]
        labels = {
            "make": "Manufacturing Company",
            "model": "Manufacturing Model",
            "year": "Manufacturing Year",
            "license_plate": "Licence plate",
        }
        widgets = {
            "make": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "min": 1900}),
            "license_plate": forms.TextInput(attrs={"class": "form-control"}),
        }
