#accounts/urls.py
from django.urls import path
from .views import UserRegistrationView, ProfileView, jwt_token_after_social_login, SocialTokenExchangeView, \
    AdminUserListView, AdminUserUpdateView, DebugHeadersView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('debug-headers/', DebugHeadersView.as_view(), name='user-profile'),

    path('jwt-social/', jwt_token_after_social_login, name='jwt-social'),
    path('social-token-exchange/', SocialTokenExchangeView.as_view(), name='social_token_exchange'),

    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', AdminUserUpdateView.as_view(), name='admin-user-update'),

]
