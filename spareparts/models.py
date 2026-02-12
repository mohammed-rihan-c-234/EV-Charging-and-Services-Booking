from django.db import models
from django.conf import settings
from decimal import Decimal

class SparePart(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True, help_text="Image URL (optional)")

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class PartOrder(models.Model):
    STATUS_CART = "cart"
    STATUS_PLACED = "placed"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PAID = "paid"
    PAYMENT_PENDING_CASH = "pending_cash"

    PAYMENT_METHOD_GPAY = "gpay"
    PAYMENT_METHOD_CASH = "cash"
    PAYMENT_METHOD_RAZORPAY = "razorpay"

    STATUS_CHOICES = [
        (STATUS_CART, "Cart"),
        (STATUS_PLACED, "Placed"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_PENDING_CASH, "Cash (to be paid)"),
    ]
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_GPAY, "GPay"),
        (PAYMENT_METHOD_CASH, "Cash"),
        (PAYMENT_METHOD_RAZORPAY, "Razorpay"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="part_orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CART)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, default="")
    razorpay_order_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    points_redeemed = models.PositiveIntegerField(default=0)
    points_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_part_orders",
    )

    def __str__(self):
        return f"Order #{self.pk} ({self.user.username})"

    def recalc_total(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.line_total
        discount = Decimal(str(self.coupon_discount)) if self.coupon_discount else Decimal("0.00")
        points_discount = Decimal(str(self.points_discount)) if self.points_discount else Decimal("0.00")
        net_total = total - discount - points_discount
        if net_total < Decimal("0.00"):
            net_total = Decimal("0.00")
        self.total_amount = net_total
        self.save(update_fields=["total_amount"])

    def get_original_total(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.line_total
        return total

    def get_discount_percentage(self):
        original = self.get_original_total()
        if original > 0:
            return int((self.coupon_discount / original) * 100)
        return 0


class PartOrderItem(models.Model):
    order = models.ForeignKey(PartOrder, on_delete=models.CASCADE, related_name="items")
    part = models.ForeignKey(SparePart, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.part.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
