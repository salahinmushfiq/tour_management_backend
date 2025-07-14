from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
        'username', 'email', 'password', 'password2', 'role', 'contact_number', 'profile_picture', 'location', 'bio')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'tourist'),
            contact_number=validated_data.get('contact_number', ''),
            profile_picture=validated_data.get('profile_picture', None),
            location=validated_data.get('location', ''),
            bio=validated_data.get('bio', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'contact_number', 'profile_picture', 'location', 'bio')
        read_only_fields = ('id', 'username', 'email', 'role')
