# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from tours.models import Guide
from .models import User
from .permissions import IsAdmin
from .serializers import UserRegistrationSerializer, UserProfileSerializer, AdminUpdateUserSerializer, UserSerializer, \
    CustomUserSerializer
from django.contrib.auth import get_user_model
import requests

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


# class UserProfileView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         serializer = CustomUserSerializer(request.user)
#         return Response(serializer.data)

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Returns the profile of the currently authenticated user,
    including role-based tours (organized, joined, guided).
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Efficiently prefetch related data depending on role
        qs = User.objects.select_related('guide').filter(id=self.request.user.id)

        role = self.request.user.role

        if role == 'organizer':
            qs = qs.prefetch_related(
                'organized_tours__guides',
                'organized_tours__offers',
                'organized_tours__tour_participants__user',
            )
        elif role == 'tourist':
            qs = qs.prefetch_related(
                'tour_participations__tour__guides',
                'tour_participations__tour__offers',
                'tour_participations__tour__tour_participants__user',
            )
        elif role == 'guide':
            qs = qs.prefetch_related(
                'guide__tours__guides',
                'guide__tours__offers',
                'guide__tours__tour_participants__user',
            )

        user = qs.get()
        return user

    def update(self, request, *args, **kwargs):
        """
        Ensure email/role cannot be updated.
        """
        restricted_fields = ['email', 'role']
        for field in restricted_fields:
            if field in request.data:
                request.data.pop(field)
        return super().update(request, *args, **kwargs)


class DebugHeadersView(APIView):
    permission_classes = []  # Public for debug

    def get(self, request):
        return Response({"headers": dict(request.headers)})


class AdminUserListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        user = self.request.user
        print("👤 Profile View Access:", user, "Is Auth:", user.is_authenticated)  # ADD LOG
        return user


class AdminUserUpdateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = AdminUpdateUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'pk'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_token_after_social_login(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


class SocialTokenExchangeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        social_token = request.data.get('social_token')
        provider = request.data.get('provider')

        if not social_token or not provider:
            return Response({"error": "Missing token or provider"}, status=400)

        # ---- GOOGLE LOGIN ----
        if provider == 'google':
            try:
                response = requests.get(
                    'https://oauth2.googleapis.com/tokeninfo',
                    params={'id_token': social_token}
                )
                if response.status_code != 200:
                    return Response({"error": "Invalid Google token"}, status=400)

                data = response.json()
                email = data.get('email')
                if not email:
                    return Response({"error": "Email not found in token"}, status=400)

                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.role = 'tourist'
                    user.login_method = 'google'
                    user.set_unusable_password()
                else:
                    user.login_method = 'google'
                user.save()

                refresh = RefreshToken.for_user(user)
                refresh['role'] = user.role
                refresh['email'] = user.email
                refresh['id'] = user.id
                refresh['login_method'] = user.login_method

                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })

            except Exception:
                return Response({"error": "Error verifying Google token"}, status=400)

        # ---- FACEBOOK LOGIN ----
        elif provider == 'facebook':
            try:
                fb_response = requests.get(
                    'https://graph.facebook.com/me',
                    params={
                        'access_token': social_token,
                        'fields': 'email'
                    }
                )
                if fb_response.status_code != 200:
                    return Response({"error": "Invalid Facebook token"}, status=400)

                data = fb_response.json()
                email = data.get('email')
                if not email:
                    return Response({"error": "Email not found in Facebook profile"}, status=400)

                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.role = 'tourist'
                    user.login_method = 'facebook'
                    user.set_unusable_password()
                else:
                    user.login_method = 'facebook'
                user.save()

                refresh = RefreshToken.for_user(user)
                refresh['role'] = user.role
                refresh['email'] = user.email
                refresh['id'] = user.id
                refresh['login_method'] = user.login_method

                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })

            except Exception:
                return Response({"error": "Error verifying Facebook token"}, status=400)

        else:
            return Response({"error": "Unsupported provider"}, status=400)
