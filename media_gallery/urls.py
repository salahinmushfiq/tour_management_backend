#media_gallery/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MediaFileViewSet

router = DefaultRouter()
router.register(r'media', MediaFileViewSet, basename='media')

urlpatterns = [
    path('', include(router.urls)),
]