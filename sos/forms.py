from django import forms
from .models import SOSAlert
from vehicles.models import Vehicle


class SOSForm(forms.ModelForm):
    """Simple form for submitting an SOS alert.

    Non-technical labels and help_texts make this easy to use.
    """
    name = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        required=True,
        empty_label="Select your vehicle",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    vehicle_model = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tesla Model 3'})
    )
    number_plate = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., DL-01-AB-1234'})
    )
    
    class Meta:
        model = SOSAlert
        fields = ['vehicle', 'address', 'latitude', 'longitude', 'message', 'contact']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your current address'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the issue'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number', 'inputmode': 'tel'}),
        }
        labels = {
            'address': 'Address',
            'message': 'Describe your issue',
            'contact': 'Contact Number',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, "is_authenticated", False):
            self.fields["vehicle"].queryset = Vehicle.objects.filter(owner=user).order_by("make", "model")
        self.fields["vehicle_model"].widget.attrs.setdefault("readonly", True)
        for field_name in ("address", "message", "contact"):
            self.fields[field_name].required = True
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False

    def clean(self):
        cleaned = super().clean()
        vehicle = cleaned.get("vehicle")
        plate = (cleaned.get("number_plate") or "").strip()
        if vehicle and not plate:
            self.add_error("number_plate", "Number plate is required.")
        return cleaned
