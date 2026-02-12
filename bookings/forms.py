from django import forms
from django.utils import timezone

from .models import ServiceBooking


class ServiceBookingForm(forms.ModelForm):
    scheduled_for = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
        help_text="Choose date and time for the service.",
    )

    class Meta:
        model = ServiceBooking
        fields = ["name", "phone_number", "service_type", "service_center", "scheduled_for", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.setdefault("class", "form-control")
        self.fields["phone_number"].widget.attrs.setdefault("class", "form-control")
        self.fields["service_type"].widget.attrs.setdefault("class", "form-select")
        self.fields["service_center"].widget.attrs.setdefault("class", "form-select")
        self.fields["scheduled_for"].widget.attrs.setdefault("class", "form-control")
        self.fields["notes"].widget.attrs.setdefault("class", "form-control")

    def clean_scheduled_for(self):
        value = self.cleaned_data["scheduled_for"]
        if value < timezone.now() - timezone.timedelta(minutes=1):
            raise forms.ValidationError("Scheduled time must be in the future.")
        return value


class BookingPaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[
            (ServiceBooking.PAYMENT_METHOD_CASH, "Cash"),
            (ServiceBooking.PAYMENT_METHOD_RAZORPAY, "Razorpay"),
        ],
        widget=forms.RadioSelect,
        initial=ServiceBooking.PAYMENT_METHOD_RAZORPAY,
    )
