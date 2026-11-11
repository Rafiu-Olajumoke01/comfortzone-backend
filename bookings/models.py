from datetime import datetime, timedelta

from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    barber = models.ForeignKey(
        "barbers.Barber",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def save(self, *args, **kwargs):
        start = datetime.combine(self.date, self.start_time)
        self.end_time = (start + timedelta(minutes=self.service.duration_minutes)).time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} with {self.barber} on {self.date} at {self.start_time}"