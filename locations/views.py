from rest_framework import viewsets, permissions
from .models import VisitedRegion
from .serializers import VisitedRegionSerializer

class VisitedRegionViewSet(viewsets.ModelViewSet):
    queryset = VisitedRegion.objects.all()
    serializer_class = VisitedRegionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)