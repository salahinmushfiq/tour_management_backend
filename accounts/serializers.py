# accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from tours.models import Tour
from tours.serializers import GuideSerializer, TourSerializer
from .models import User
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'role', 'contact_number', 'profile_picture', 'location', 'bio')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


# ------------------------------
# User Profile Serializer (Full)
# ------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    guide = GuideSerializer(read_only=True)
    organized_tours = serializers.SerializerMethodField()
    joined_tours = serializers.SerializerMethodField()
    guided_tours = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'bio', 'contact_number', 'profile_picture',
            'location', 'guide', 'organized_tours', 'joined_tours', 'guided_tours'
        ]
        read_only_fields = ('id', 'email', 'role')

    # ------------------------------
    # Organized Tours (Organizers)
    # ------------------------------
    def get_organized_tours(self, obj):
        if obj.role == 'organizer':
            tours = obj.organized_tours.prefetch_related(
                'guides', 'offers', 'tour_participants__user'
            )
            return TourSerializer(tours, many=True).data
        return []

    # ------------------------------
    # Joined Tours (Tourists)
    # ------------------------------
    def get_joined_tours(self, obj):
        if obj.role == 'tourist':
            tours = Tour.objects.filter(
                tour_participants__user=obj
            ).prefetch_related(
                'guides', 'offers', 'tour_participants__user'
            ).distinct()
            return TourSerializer(tours, many=True).data
        return []

    # ------------------------------
    # Guided Tours (Guides)
    # ------------------------------
    def get_guided_tours(self, obj):
        if obj.role == 'guide' and hasattr(obj, 'guide'):
            tours = obj.guide.tours.prefetch_related(
                'guides', 'offers', 'tour_participants__user'
            )
            return TourSerializer(tours, many=True).data
        return []


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password')  # no username


class CustomUserSerializer(UserSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'role','user_name')

    def get_user_name(self, obj):
        return obj.username or obj.email.split('@')[0]


class AdminUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role', 'is_active']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Reload the user to ensure all fields (e.g., role) are present
        user = User.objects.get(pk=user.pk)

        token['role'] = user.role  # Now this will work
        token['login_method'] = user.login_method
        token['email'] = user.email
        token['id'] = user.id
        return token
