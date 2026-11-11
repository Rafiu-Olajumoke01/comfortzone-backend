from django.urls import path

from .views import (
    AvailabilityView,
    BookingListCreateView,
    CancelBookingView,
    UpdateBookingStatusView,
)

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list"),
    path("availability/", AvailabilityView.as_view(), name="booking-availability"),
    path("<int:pk>/cancel/", CancelBookingView.as_view(), name="booking-cancel"),
    path("<int:pk>/status/", UpdateBookingStatusView.as_view(), name="booking-status"),
]