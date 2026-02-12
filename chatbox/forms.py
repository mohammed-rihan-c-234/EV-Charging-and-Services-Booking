from django import forms
from service_center.models import ServiceCenter


class NewChatMessageForm(forms.Form):
    """A minimal form for posting a chat message."""
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Type your message..."}),
        label="Message",
    )


class NewChatSessionForm(forms.Form):
    service_center = forms.ModelChoiceField(
        queryset=ServiceCenter.objects.all().order_by("name"),
        empty_label="Select service center",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Service Center",
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Type your message..."}),
        label="Message",
    )
