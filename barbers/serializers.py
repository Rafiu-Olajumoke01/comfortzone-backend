from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Barber


class BarberSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Barber
        fields = ("id", "first_name", "last_name", "bio", "photo", "is_active")
        read_only_fields = ("id", "is_active")

    class BarberCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(username__iexact=value).exists() or User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            role="barber",
        )
        return Barber.objects.create(user=user, bio=validated_data.get("bio", ""))