# costs/views.py
from rest_framework import viewsets, permissions
from .models import CostEntry
from .serializers import CostEntrySerializer


class CostEntryViewSet(viewsets.ModelViewSet):
    queryset = CostEntry.objects.all()
    serializer_class = CostEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
