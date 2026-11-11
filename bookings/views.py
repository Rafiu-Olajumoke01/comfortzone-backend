from datetime import date as date_type, datetime, time, timedelta

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny

from barbers.models import Barber
from services.models import Service
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingSerializer


def visible_bookings(user):
    queryset = Booking.objects.select_related("barber__user", "service")
    if user.role == "admin":
        return queryset
    if user.role == "barber":
        return queryset.filter(barber__user=user)
    return queryset.filter(customer=user)


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        return visible_bookings(self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class CancelBookingView(APIView):
    def post(self, request, pk):
        booking = get_object_or_404(visible_bookings(request.user), pk=pk)
        if booking.status in (Booking.Status.COMPLETED, Booking.Status.CANCELLED):
            return Response({"detail": "This booking can no longer be cancelled."}, status=400)
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data)

class AvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            barber = Barber.objects.get(pk=request.query_params["barber"], is_active=True)
            service = Service.objects.get(pk=request.query_params["service"], is_active=True)
            day = date_type.fromisoformat(request.query_params["date"])
        except (KeyError, ValueError, Barber.DoesNotExist, Service.DoesNotExist):
            return Response({"detail": "Provide a valid barber, service and date (YYYY-MM-DD)."}, status=400)

        open_at = datetime.combine(day, time(8, 0))
        close_at = datetime.combine(day, time(18, 0))
        step = timedelta(minutes=30)
        length = timedelta(minutes=service.duration_minutes)

        booked = list(
            Booking.objects.filter(barber=barber, date=day)
            .exclude(status=Booking.Status.CANCELLED)
            .values_list("start_time", "end_time")
        )

        slots = []
        current = open_at
        while current + length <= close_at:
            start = current.time()
            end = (current + length).time()
            if not any(start < b_end and end > b_start for b_start, b_end in booked):
                slots.append(start.strftime("%H:%M"))
            current += step
        return Response({"date": day.isoformat(), "slots": slots})

class UpdateBookingStatusView(APIView):
    def post(self, request, pk):
        if request.user.role not in ("barber", "admin"):
            return Response({"detail": "Not allowed."}, status=403)
        booking = get_object_or_404(visible_bookings(request.user), pk=pk)
        new_status = request.data.get("status")
        allowed = {
            Booking.Status.PENDING: [Booking.Status.CONFIRMED],
            Booking.Status.CONFIRMED: [Booking.Status.COMPLETED],
        }
        if new_status not in allowed.get(booking.status, []):
            return Response(
                {"detail": f"Cannot change a {booking.status} booking to {new_status}."},
                status=400,
            )
        booking.status = new_status
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data)