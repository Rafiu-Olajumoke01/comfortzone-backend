from django.urls import path

from .views import AdminTeamView, BarberDetailView, BarberListView, MyBarberProfileView

urlpatterns = [
    path("", BarberListView.as_view(), name="barber-list"),
    path("me/", MyBarberProfileView.as_view(), name="barber-me"),
    path("<int:pk>/", BarberDetailView.as_view(), name="barber-detail"),
    path("admin/team/", AdminTeamView.as_view(), name="barber-admin-team"),
]