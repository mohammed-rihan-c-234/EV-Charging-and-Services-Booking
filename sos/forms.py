from django import forms
from .models import SOSAlert


class SOSForm(forms.ModelForm):
    """Simple form for submitting an SOS alert.

    Non-technical labels and help_texts make this easy to use.
    """
    name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    vehicle_model = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tesla Model 3'})
    )
    number_plate = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., DL-01-AB-1234'})
    )
    
    class Meta:
        model = SOSAlert
        fields = ['latitude', 'longitude', 'message', 'contact']
        widgets = {
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'inputmode': 'decimal'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'inputmode': 'decimal'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the issue'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number', 'inputmode': 'tel'}),
        }
        labels = {
            'latitude': 'Latitude (optional)',
            'longitude': 'Longitude (optional)',
            'message': 'Describe your issue',
            'contact': 'Contact Number',
        }
