#locations/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import VisitedRegionViewSet

router = DefaultRouter()
router.register(r'regions', VisitedRegionViewSet, basename='regions')

urlpatterns = [
    path('', include(router.urls)),
]