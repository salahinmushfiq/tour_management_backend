from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GuideViewSet, TourViewSet, OfferViewSet, TourParticipantViewSet

router = DefaultRouter()
router.register(r'guides', GuideViewSet, basename='guide')
router.register(r'tours', TourViewSet, basename='tour')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'participants', TourParticipantViewSet, basename='participant')

urlpatterns = [
    path('', include(router.urls)),
]
