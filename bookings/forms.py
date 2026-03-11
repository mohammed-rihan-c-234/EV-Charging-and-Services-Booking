from django import forms
from django.utils import timezone

from accounts.models import Profile
from service_center.models import ServiceCenter
from vehicles.models import Vehicle

from .models import ServiceBooking


class ServiceBookingForm(forms.ModelForm):
    scheduled_for = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
        help_text="Choose date and time for the service.",
    )

    class Meta:
        model = ServiceBooking
        fields = ["name", "phone_number", "vehicle", "service_type", "service_center", "scheduled_for", "notes"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.setdefault("class", "form-control")
        self.fields["phone_number"].widget.attrs.setdefault("class", "form-control")
        self.fields["phone_number"].max_length = 10
        self.fields["phone_number"].min_length = 10
        self.fields["phone_number"].widget.attrs["inputmode"] = "numeric"
        self.fields["phone_number"].widget.attrs["maxlength"] = "10"
        self.fields["phone_number"].widget.attrs["minlength"] = "10"
        self.fields["phone_number"].widget.attrs["pattern"] = r"[0-9]{10}"
        self.fields["vehicle"].widget.attrs.setdefault("class", "form-select")
        self.fields["service_type"].widget.attrs.setdefault("class", "form-select")
        self.fields["service_center"].widget.attrs.setdefault("class", "form-select")
        self.fields["scheduled_for"].widget.attrs.setdefault("class", "form-control")
        # Block previous date/time values in the calendar input.
        self.fields["scheduled_for"].widget.attrs["min"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")
        self.fields["notes"].widget.attrs.setdefault("class", "form-control")
        self.fields["service_center"].queryset = ServiceCenter.objects.all().order_by("name")
        if user and getattr(user, "is_authenticated", False):
            self.fields["vehicle"].queryset = Vehicle.objects.for_user(user).order_by("make", "model")
        else:
            self.fields["vehicle"].queryset = Vehicle.objects.none()
        self.fields["vehicle"].empty_label = "Select your vehicle"
        self.fields["vehicle"].required = True
        if user and getattr(user, "is_authenticated", False) and not self.is_bound:
            try:
                profile = user.profile  # type: ignore[attr-defined]
            except Profile.DoesNotExist:
                profile = None
            if profile:
                if not self.initial.get("name"):
                    self.initial["name"] = profile.full_name or ""
                if not self.initial.get("phone_number"):
                    self.initial["phone_number"] = profile.phone_number or ""

    def clean_vehicle(self):
        value = self.cleaned_data.get("vehicle")
        if value is None:
            raise forms.ValidationError("Please select a vehicle.")
        return value

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if not value:
            raise forms.ValidationError("Phone number is required.")
        if not value.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return value

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
