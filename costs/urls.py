from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CostEntryViewSet

router = DefaultRouter()
router.register(r'costs', CostEntryViewSet, basename='costs')

urlpatterns = [
    path('', include(router.urls)),
]