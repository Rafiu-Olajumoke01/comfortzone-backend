from rest_framework import generics
from rest_framework.permissions import AllowAny

from services.views import IsAdmin

from .models import GalleryImage
from .serializers import GalleryImageSerializer


class GalleryListView(generics.ListAPIView):
    queryset = GalleryImage.objects.filter(is_active=True)
    serializer_class = GalleryImageSerializer
    permission_classes = [AllowAny]


class AdminGalleryListCreateView(generics.ListCreateAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdmin]


class AdminGalleryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdmin]