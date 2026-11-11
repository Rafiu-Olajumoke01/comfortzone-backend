from django.urls import path

from .views import (
    AdminServiceDetailView,
    AdminServiceListCreateView,
    ServiceDetailView,
    ServiceListView,
)
urlpatterns = [
    path("", ServiceListView.as_view(), name="service-list"),
    path("<int:pk>/", ServiceDetailView.as_view(), name="service-detail"),
    path("admin/", AdminServiceListCreateView.as_view(), name="service-admin-list"),
    path("admin/<int:pk>/", AdminServiceDetailView.as_view(), name="service-admin-detail"),
]