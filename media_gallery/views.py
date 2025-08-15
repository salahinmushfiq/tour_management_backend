# media_gallery/views.py
from rest_framework import viewsets, permissions
from .models import MediaFile
from .serializers import MediaFileSerializer

class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)