from django.conf import settings
from django.db import models


class Barber(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="barber_profile",
        limit_choices_to={"role": "barber"},
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="barbers/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)