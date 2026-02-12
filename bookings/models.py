from django.conf import settings
from django.db import models
from django.utils import timezone


class ServiceBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    APPROVAL_PENDING = "pending"
    APPROVAL_ACCEPTED = "accepted"
    APPROVAL_REJECTED = "rejected"
    APPROVAL_CHOICES = [
        (APPROVAL_PENDING, "Pending"),
        (APPROVAL_ACCEPTED, "Accepted"),
        (APPROVAL_REJECTED, "Rejected"),
    ]

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_PENDING_CASH = "pending_cash"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_PENDING_CASH, "Cash (to be paid)"),
    ]
    PAYMENT_METHOD_GPAY = "gpay"
    PAYMENT_METHOD_CASH = "cash"
    PAYMENT_METHOD_RAZORPAY = "razorpay"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_GPAY, "GPay"),
        (PAYMENT_METHOD_CASH, "Cash"),
        (PAYMENT_METHOD_RAZORPAY, "Razorpay"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_bookings",
    )
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)

    service_type = models.ForeignKey(
        "services.ServiceType",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    service_center = models.ForeignKey(
        "service_center.ServiceCenter",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.PROTECT,
        related_name="service_bookings",
        null=True,
        blank=True,
    )

    scheduled_for = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, default="")
    razorpay_order_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default=APPROVAL_PENDING)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_service_bookings",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_for", "-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.service_type} @ {self.service_center} ({self.scheduled_for:%Y-%m-%d %H:%M})"

    def get_original_amount(self):
        return self.amount + self.coupon_discount

    def get_discount_percentage(self):
        original = self.get_original_amount()
        if original > 0:
            return int((self.coupon_discount / original) * 100)
        return 0

# Create your models here.
