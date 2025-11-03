# tour_management/urls.py
from django.contrib import admin
from django.urls import path, include
from tour_management.views import robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts app endpoints
    path('api/accounts/', include('accounts.urls')),

    # Djoser auth endpoints
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),

    # Placeholder for other app endpoints
    path('api/tours/', include('tours.urls')),
    path('api/media/', include('media_gallery.urls')),
    path('api/costs/', include('costs.urls')),
    path('api/locations/', include('locations.urls')),
    # path('auth/', include('djoser.urls.jwt')),
    path('social-auth/', include('social_django.urls', namespace='social')),  # <- This line!
    path("robots.txt", robots_txt),


]