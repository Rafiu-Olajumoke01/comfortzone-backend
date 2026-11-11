from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attendance, ShopLocation

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Extra", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Extra", {"fields": ("email", "role", "phone")}),)
    list_display = ("username", "email", "role", "is_staff")

@admin.register(ShopLocation)
class ShopLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "radius_meters", "enforce")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("barber", "signed_in_at", "distance_meters")
    list_filter = ("barber", "signed_in_at")
    readonly_fields = ("signed_in_at",)