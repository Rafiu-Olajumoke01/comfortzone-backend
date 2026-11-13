from rest_framework import serializers

from .models import Barber


class BarberSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Barber
        fields = ("id", "first_name", "last_name", "bio", "photo", "is_active")
        read_only_fields = ("id", "is_active")