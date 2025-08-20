# tours/serializers.py
from rest_framework import serializers
from .models import (
    Guide, Tour, Offer, TourParticipant,
    TourChatMessage, TourRating, TourGuideAssignment
)


# ------------------------------
# Basic Serializers
# ------------------------------
class GuideSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Guide
        fields = ['id', 'user_email', 'user_name', 'bio', 'contact_number', 'profile_picture']


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'discount_percent', 'valid_from', 'valid_until']


class ParticipantSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = TourParticipant
        fields = ['id', 'email', 'role', 'joined_at', 'is_active', 'status']
        read_only_fields = ['joined_at']


class MyTourSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.email", read_only=True)
    participants_count = serializers.SerializerMethodField()
    # guides = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            # "location",
            "organizer_name",
            "participants_count",
            # "guides",
            "status",
            "cover_image"
        ]

    def get_participants_count(self, obj):
        return obj.participants.count()

    # def get_guides(self, obj):
    #     # Return a list of assigned guides
    #     return [assignment.guide.email for assignment in obj.guides.all()]

    def get_status(self, obj):
        user = self.context['request'].user
        try:
            participant = obj.tour_participants.get(user=user)
            return participant.status
        except TourParticipant.DoesNotExist:
            return None


class TourGuideAssignmentSerializer(serializers.ModelSerializer):
    guide_email = serializers.EmailField(source="guide.email", read_only=True)
    tour_title = serializers.CharField(source="tour.title", read_only=True)
    # guide = GuideSerializer(read_only=True)  # nest guide info here
    guide_profile = GuideSerializer(source="guide.guide", read_only=True)

    class Meta:
        model = TourGuideAssignment
        fields = [
            "id", "tour", "tour_title", "guide", "guide_email",
            "status", "assigned_at", "responded_at", "guide_profile"
        ]
        read_only_fields = ["assigned_at", "responded_at"]


# ------------------------------
# Tour Serializer (Full Data)
# ------------------------------
class TourSerializer(serializers.ModelSerializer):
    organizer_email = serializers.EmailField(source='organizer.email', read_only=True)
    organizer = serializers.StringRelatedField(read_only=True)
    # guides = GuideSerializer(many=True)
    guides = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'organizer', 'title', 'description', 'start_date', 'end_date',
            'organizer_email',  # for consistent access in frontend
            'start_location', 'end_location', 'is_custom_group', 'max_participants',
            'cost_per_person', 'cover_image', 'category',
            'guides', 'participants', 'offers', 'status'
        ]

    def get_participants(self, obj):
        # Include all participants for the tour
        participants = obj.tour_participants.select_related('user').all()
        return ParticipantSerializer(participants, many=True).data

    def get_status(self, tour):
        user = self.context.get("user")
        if not user:
            return None
        try:
            participant = tour.tour_participants.filter(user=user).first()
            return participant.status if participant else None
        except TourParticipant.DoesNotExist:
            return None

    def get_guides(self, obj):
        # Only accepted guides show up
        # Only accepted guides show up
        assignments = obj.guide_assignments.filter(
            status="accepted"
        ).select_related("guide__guide")  # ✅ loads User and its Guide profile in one query

        return [
            GuideSerializer(assignment.guide.guide, context=self.context).data
            for assignment in assignments
            if hasattr(assignment.guide, "guide")  # ensure profile exists
        ]

# ------------------------------
# New Serializers for Chats & Ratings
# ------------------------------

class TourChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)

    class Meta:
        model = TourChatMessage
        fields = ['id', 'tour', 'sender', 'sender_email', 'message', 'created_at']


class TourRatingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TourRating
        fields = ['id', 'tour', 'user', 'user_email', 'rating', 'review', 'created_at']
        read_only_fields = ['created_at']
