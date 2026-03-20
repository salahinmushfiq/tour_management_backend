# bookings/serializers.py
from rest_framework import serializers
from payments.serializers import PaymentSerializer
from tours.serializers import TourSerializer, ParticipantSerializer
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    tour = TourSerializer(source='participant.tour', read_only=True)
    participant_user = ParticipantSerializer(source='participant', read_only=True)
    payments = serializers.SerializerMethodField()
    latest_payment_method = serializers.SerializerMethodField()
    latest_payment_time = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_payments(self, obj):
        payments_qs = obj.payments.all().order_by('-created_at')
        return PaymentSerializer(payments_qs, many=True).data

    def get_latest_payment_method(self, obj):
        latest_payment = obj.payments.order_by("-created_at").first()
        return latest_payment.method if latest_payment else None

    def get_latest_payment_time(self, obj):
        latest_payment = obj.payments.order_by("-created_at").first()
        return latest_payment.created_at if latest_payment else None
