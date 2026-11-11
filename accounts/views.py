from math import asin, cos, radians, sin, sqrt

from django.utils import timezone
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework import serializers

from .models import Attendance, ShopLocation
from .serializers import ChangePasswordSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def distance_in_meters(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return int(2 * r * asin(sqrt(a)))


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Lets users log in with their email, and returns their profile with the tokens."""

    def validate(self, attrs):
        email = (attrs.get("username") or "").strip()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            attrs["username"] = user.get_username()
        data = super().validate(attrs)

        if self.user.role == User.Role.BARBER:
            request = self.context["request"]
            lat = to_float(request.data.get("latitude"))
            lng = to_float(request.data.get("longitude"))
            shop = ShopLocation.objects.first()
            distance = None

            if shop and lat is not None and lng is not None:
                distance = distance_in_meters(
                    float(shop.latitude), float(shop.longitude), lat, lng
                )

            if shop and shop.enforce:
                if distance is None:
                    raise serializers.ValidationError(
                        {"detail": "Allow location access to sign in."}
                    )
                if distance > shop.radius_meters:
                    raise serializers.ValidationError(
                        {"detail": "You must be at the shop to sign in."}
                    )

            Attendance.objects.create(
                barber=self.user,
                latitude=lat,
                longitude=lng,
                distance_meters=distance,
            )

        data["user"] = UserSerializer(self.user).data
        return data


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TodayAttendanceView(APIView):
    def get(self, request):
        first = (
            Attendance.objects.filter(
                barber=request.user,
                signed_in_at__date=timezone.localdate(),
            )
            .order_by("signed_in_at")
            .first()
        )
        return Response(
            {"signed_in_at": first.signed_in_at if first else None}
        )


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password changed."})