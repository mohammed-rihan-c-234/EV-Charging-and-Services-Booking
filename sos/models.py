from django.db import models
from django.conf import settings
from vehicles.models import Vehicle
from service_center.models import ServiceCenter
from django.utils import timezone

class SOSAlert(models.Model):
    """An SOS alert sent by a user or device with location."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('ack', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    message = models.TextField(blank=True)
    # optional free-form plate and contact fields for device alerts
    vehicle_plate = models.CharField(max_length=32, null=True, blank=True)
    contact = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"SOS {self.pk} - {self.status}"


class AssignedCenter(models.Model):
    """Record that a ServiceCenter was assigned/notified for an SOS alert."""
    alert = models.ForeignKey(SOSAlert, on_delete=models.CASCADE, related_name='assigned_centers')
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
    distance_km = models.DecimalField(max_digits=8, decimal_places=3)
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['distance_km']

    def __str__(self):
        return f"Alert {self.alert_id} -> {self.center.name} ({self.distance_km} km)"
