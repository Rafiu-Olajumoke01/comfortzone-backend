from datetime import datetime, time, timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    barber_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source="service.name", read_only=True)
    customer_name = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    service_price = serializers.DecimalField(
        source="service.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Booking
        fields = (
            "id", "customer_name", "customer_phone", "barber", "barber_name", "service",
            "service_name", "service_price",
            "date", "start_time", "end_time", "status", "is_paid", "notes", "created_at",
        )
        read_only_fields = ("id", "end_time", "status", "created_at")

    def get_barber_name(self, obj):
        return obj.barber.user.get_full_name() or obj.barber.user.username

    def get_customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username

    def get_is_paid(self, obj):
        return obj.payments.filter(status="success").exists()

    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Date cannot be in the past.")
        return value

    def validate_barber(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This barber is not available.")
        return value

    def validate_service(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This service is not available.")
        return value

    def validate(self, attrs):
        barber = attrs["barber"]
        date = attrs["date"]
        start = attrs["start_time"]
        service = attrs["service"]

        end_dt = datetime.combine(date, start) + timedelta(minutes=service.duration_minutes)
        if end_dt.date() != date:
            raise serializers.ValidationError("Booking must end on the same day it starts.")
        end = end_dt.time()

        if start < time(8, 0) or end > time(18, 0):
            raise serializers.ValidationError("Bookings are only available between 08:00 and 18:00.")

        clash = (
            Booking.objects.filter(barber=barber, date=date)
            .exclude(status=Booking.Status.CANCELLED)
            .filter(start_time__lt=end, end_time__gt=start)
        )
        if clash.exists():
            raise serializers.ValidationError("This barber is already booked at that time.")

        attrs["end_time"] = end
        return attrs