from rest_framework import serializers
from .models import Guide, Tour, Offer, TourParticipant
from accounts.serializers import UserProfileSerializer  # for nested user info if needed

class GuideSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Guide
        fields = ['id', 'user', 'bio', 'contact_number', 'profile_picture']

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'discount_percent', 'valid_from', 'valid_until']

class TourSerializer(serializers.ModelSerializer):
    guide = GuideSerializer(read_only=True)
    offers = OfferSerializer(many=True, read_only=True)
    organizer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tour
        fields = [
            'id', 'organizer', 'title', 'description', 'start_date', 'end_date',
            'start_location', 'end_location', 'is_custom_group', 'max_participants',
            'guide', 'cost_per_person', 'offers',
        ]

class TourParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    tour = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TourParticipant
        fields = ['id', 'tour', 'user', 'joined_at', 'is_active']
