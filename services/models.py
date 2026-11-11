from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)
    image = models.ImageField(upload_to="services/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name