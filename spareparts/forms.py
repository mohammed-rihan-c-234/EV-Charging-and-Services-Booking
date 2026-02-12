from django import forms

from service_center.models import ServiceCenter


class PaymentChoiceForm(forms.Form):
    PAYMENT_CASH = "cash"
    PAYMENT_RAZORPAY = "razorpay"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_RAZORPAY, "Razorpay"),
    ]

    service_center = forms.ModelChoiceField(
        queryset=ServiceCenter.objects.all(),
        empty_label="Select service center",
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial=PAYMENT_RAZORPAY,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_center"].widget.attrs.setdefault("class", "form-select")
