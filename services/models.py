from django.db import models

class ServiceType(models.Model):
    """A type of EV-related service (charging, maintenance, towing)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
