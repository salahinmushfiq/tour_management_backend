from rest_framework import viewsets, permissions
from .models import Guide, Tour, Offer, TourParticipant
from .serializers import GuideSerializer, TourSerializer, OfferSerializer, TourParticipantSerializer

class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = [permissions.IsAuthenticated]

class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the logged-in user as the organizer
        serializer.save(organizer=self.request.user)

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]

class TourParticipantViewSet(viewsets.ModelViewSet):
    queryset = TourParticipant.objects.all()
    serializer_class = TourParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Assign logged-in user as participant
        serializer.save(user=self.request.user)
from django.shortcuts import render

# Create your views here.
