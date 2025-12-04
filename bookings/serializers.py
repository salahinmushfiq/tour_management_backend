# bookings/serializers.py
from rest_framework import serializers
from payments.models import Payment
from tours.serializers import TourSerializer, ParticipantSerializer
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    tour = TourSerializer(source='participant.tour', read_only=True)
    participant_user = ParticipantSerializer(source='participant', read_only=True)
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_payments(self, obj):
        from payments.serializers import PaymentSerializer
        payments_qs = obj.payments.all().order_by('-created_at')
        return PaymentSerializer(payments_qs, many=True).data