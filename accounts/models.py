from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BARBER = "barber", "Barber"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

class ShopLocation(models.Model):
    name = models.CharField(max_length=100, default="Comfort Zone")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=6.672624)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=3.455622)
    radius_meters = models.PositiveIntegerField(default=150)
    enforce = models.BooleanField(
        default=False,
        help_text="Turn on so barbers can only sign in at the shop.",
    )

    def __str__(self):
        return self.name


class Attendance(models.Model):
    barber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance",
    )
    signed_in_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    distance_meters = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-signed_in_at"]

    def __str__(self):
        return f"{self.barber} - {self.signed_in_at:%Y-%m-%d %H:%M}"