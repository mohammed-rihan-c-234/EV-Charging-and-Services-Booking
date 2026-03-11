from django.db import models
from django.conf import settings

class ChargingStation(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    available_slots = models.PositiveSmallIntegerField(default=0)
    plug_types = models.CharField(max_length=200, blank=True, help_text='Comma-separated plug types')
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)

    def __str__(self):
        return f"{self.name} ({self.available_slots} slots)"


class ChargingBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_PENDING = "pending"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_PENDING, "Pending Payment"),
    ]

    PAYMENT_METHOD_RAZORPAY = "razorpay"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_RAZORPAY, "Razorpay"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="charging_bookings")
    station = models.ForeignKey(ChargingStation, on_delete=models.PROTECT, related_name="bookings")
    duration_hours = models.PositiveIntegerField(default=2)
    scheduled_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, default="")
    razorpay_order_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    points_redeemed = models.PositiveIntegerField(default=0)
    points_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Charging at {self.station.name} - {self.scheduled_at:%Y-%m-%d %H:%M}"

    def calculate_amount(self):
        return self.duration_hours * self.station.price_per_hour

    class Meta:
        ordering = ["-scheduled_at", "-created_at"]
