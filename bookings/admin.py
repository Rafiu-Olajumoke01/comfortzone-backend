from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "barber", "service", "date", "start_time", "status")
    list_filter = ("status", "date", "barber")