# tour_management/urls.py
from django.contrib import admin
from django.urls import path, include
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#
#     path('api/accounts/', include('accounts.urls')),  # Your accounts app urls if any
#
#     # Djoser authentication endpoints
#     path('api/auth/', include('djoser.urls')),
#     path('api/auth/', include('djoser.urls.jwt')),
#
#     # Other app endpoints
#     path('api/tours/', include('tours.urls')),
#     path('api/media/', include('media_gallery.urls')),
#     path('api/costs/', include('costs.urls')),
#     path('api/locations/', include('locations.urls')),
#
#     # Social auth endpoints (for OAuth login redirects etc)
#     path('social-auth/', include('social_django.urls', namespace='social')),
# ]
#
# tour_management/urls.py
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


# from django.contrib import admin
# from django.urls import path, include
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#
#     # Accounts & Auth
#     path('api/accounts/', include('accounts.urls')),  # ✅ now includes cookie JWT
#
#     # If you still want Djoser for password reset & registration:
#     path('api/auth/', include('djoser.urls')),  # e.g. /users/, /users/reset_password/
#
#     # Your app APIs
#     path('api/tours/', include('tours.urls')),
#     path('api/media/', include('media_gallery.urls')),
#     path('api/costs/', include('costs.urls')),
#     path('api/locations/', include('locations.urls')),
#
#     # Optional: Django social-auth (redirect-based OAuth)
#     path('social-auth/', include('social_django.urls', namespace='social')),
# ]
