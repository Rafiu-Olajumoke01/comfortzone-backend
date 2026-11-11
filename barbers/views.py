from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny, BasePermission
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Attendance
from services.views import IsAdmin

from .models import Barber
from .serializers import BarberSerializer


class IsBarber(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "barber")


class BarberListView(generics.ListAPIView):
    queryset = Barber.objects.filter(is_active=True).select_related("user")
    serializer_class = BarberSerializer
    permission_classes = [AllowAny]


class BarberDetailView(generics.RetrieveAPIView):
    queryset = Barber.objects.filter(is_active=True).select_related("user")
    serializer_class = BarberSerializer
    permission_classes = [AllowAny]


class MyBarberProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BarberSerializer
    permission_classes = [IsBarber]

    def get_object(self):
        return get_object_or_404(Barber, user=self.request.user)
    

class AdminTeamView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.localdate()
        data = []
        for barber in Barber.objects.filter(is_active=True).select_related("user"):
            first = (
                Attendance.objects.filter(barber=barber.user, signed_in_at__date=today)
                .order_by("signed_in_at")
                .first()
            )
            data.append(
                {
                    "id": barber.id,
                    "name": barber.user.get_full_name() or barber.user.username,
                    "clocked_in": first is not None,
                    "since": timezone.localtime(first.signed_in_at).strftime("%H:%M") if first else None,
                }
            )
        return Response(data)