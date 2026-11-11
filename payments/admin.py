from django.contrib import admin

from .models import Payment, PaymentAccount


@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_name", "account_number", "is_active")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "booking", "amount", "status", "paid_at")
    list_filter = ("status",)