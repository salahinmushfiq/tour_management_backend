# payments/serializers.py
from rest_framework import serializers
from .models import Payment
from bookings.models import Booking
from tours.serializers import ParticipantSerializer
from decimal import Decimal


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "amount", "method"]

    def validate(self, attrs):
        booking = attrs.get("booking")
        amount = attrs.get("amount")
        method = attrs.get("method")

        if amount is None or amount <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")

        if booking.payment_status == "paid":
            raise serializers.ValidationError("Booking is already fully paid.")

        # ensure participant is approved for that booking
        participant = booking.participant
        if getattr(participant, "status", None) != "approved":
            raise serializers.ValidationError("Participant must be approved before payment.")

        # don't allow amount greater than due by default
        due = booking.amount - (booking.amount_paid or Decimal("0"))
        if amount > due:
            raise serializers.ValidationError(f"Amount greater than due ({due}).")

        # method validation
        if method not in dict(Payment.METHOD_CHOICES).keys():
            raise serializers.ValidationError("Invalid payment method.")

        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(read_only=True)
    booking_detail = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    verified_by_email = serializers.EmailField(source="verified_by.email", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "status",
            "transaction_id",
            "gateway_payload",
            "created_at",
            "updated_at",
            "verified_by",
            "verified_at",
        ]

    def get_booking_detail(self, obj):
        # return a minimal booking summary
        return {
            "id": obj.booking.id,
            "participant_id": obj.booking.participant.id,
            "amount": str(obj.booking.amount),
            "amount_paid": str(obj.booking.amount_paid),
            "payment_status": obj.booking.payment_status,
        }
