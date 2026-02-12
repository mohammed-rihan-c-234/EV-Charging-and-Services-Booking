from django.contrib import admin

from .models import ServiceBooking


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "scheduled_for",
        "service_type",
        "service_center",
        "name",
        "phone_number",
        "amount",
        "payment_status",
        "payment_method",
        "approval_status",
        "status",
    )
    list_filter = ("status", "approval_status", "payment_status", "payment_method", "service_center", "service_type")
    search_fields = ("name", "phone_number", "user__username", "service_center__name", "service_type__name")

# Register your models here.
