from django import forms


class PaymentChoiceForm(forms.Form):
    PAYMENT_CASH = "cash"
    PAYMENT_RAZORPAY = "razorpay"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_RAZORPAY, "Razorpay"),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial=PAYMENT_RAZORPAY,
    )
