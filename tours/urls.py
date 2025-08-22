# tours/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GuideViewSet, TourViewSet, OfferViewSet, TourParticipantViewSet, TourGuideAssignmentViewSet, \
    TouristToursView, dashboard_stats

router = DefaultRouter()
router.register(r'guides', GuideViewSet, basename='guide')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'participants', TourParticipantViewSet, basename='participant')
# router.register(r'participants/my-tours', MyToursViewSet, basename='my-tours')
router.register(r'tour-guide-assignments', TourGuideAssignmentViewSet, basename='tour-guide-assignment')
router.register(r'', TourViewSet, basename='tour')
urlpatterns = [
    path('my-tours/', TouristToursView.as_view(), name='my-tours'),  # manual APIView path
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('', include(router.urls)),
]
