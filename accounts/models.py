from django.conf import settings
from django.db import models
from service_center.models import ServiceCenter


class Profile(models.Model):
    ROLE_USER = "user"
    ROLE_SERVICE_CENTER = "service_center"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_SERVICE_CENTER, "Service Center"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_USER)
    service_center = models.ForeignKey(
        ServiceCenter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="profiles",
    )

    def __str__(self) -> str:
        return f"{self.full_name} ({self.user.username})"

# Create your models here.
