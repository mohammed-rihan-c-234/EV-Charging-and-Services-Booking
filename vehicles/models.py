"""Simple models for storing EV vehicles."""
from django.db import models
from django.conf import settings


class VehicleQuerySet(models.QuerySet):
    def for_user(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return self.none()
        if getattr(user, "is_staff", False):
            return self
        return self.filter(owner=user)


class Vehicle(models.Model):
    """A vehicle that can use the EV services.

    Fields are kept basic for clarity.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )
    owner_name = models.CharField(max_length=100)
    make = models.CharField(max_length=100, help_text='Manufacturer, e.g., Tesla')
    model = models.CharField(max_length=100, help_text='Model name, e.g., Model 3')
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)
    objects = VehicleQuerySet.as_manager()

    def __str__(self):
        return f"{self.make} {self.model} ({self.owner_name})"

    def get_absolute_url(self):
        """Return a simple URL to this vehicle's detail page.

        This helps templates link to a vehicle's detail view.
        """
        return f"/vehicles/{self.pk}/"
