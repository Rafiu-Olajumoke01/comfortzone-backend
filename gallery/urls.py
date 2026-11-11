from django.urls import path

from .views import AdminGalleryDetailView, AdminGalleryListCreateView, GalleryListView

urlpatterns = [
    path("", GalleryListView.as_view(), name="gallery-list"),
    path("admin/", AdminGalleryListCreateView.as_view(), name="gallery-admin-list"),
    path("admin/<int:pk>/", AdminGalleryDetailView.as_view(), name="gallery-admin-detail"),
]