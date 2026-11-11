from django.contrib import admin

from .models import Barber


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active")