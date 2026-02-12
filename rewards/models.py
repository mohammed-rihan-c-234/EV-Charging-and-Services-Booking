from django.db import models
from django.conf import settings

class RewardAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"
