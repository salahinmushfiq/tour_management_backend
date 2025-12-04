# bookings/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils import timezone
from tours.models import TourParticipant
from .models import Booking
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404
from decimal import Decimal
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


# Create your views here.

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # ---------------------------
    # ✅ Queryset with correct filtering
    # ---------------------------
    def get_queryset(self):
        qs = Booking.objects.all()
        user = self.request.user

        # Role-based scope control
        if user.role == "admin":
            pass  # full access
        elif user.role == "organizer":
            qs = qs.filter(participant__tour__organizer=user)
        else:  # tourist
            qs = qs.filter(participant__user=user)

        # ✅ Optional filters that frontend sends
        participant_user = self.request.query_params.get("participant_user")
        tour = self.request.query_params.get("tour")

        if participant_user:
            qs = qs.filter(participant__user_id=participant_user)

        if tour:
            qs = qs.filter(participant__tour_id=tour)

        return qs

    # ---------------------------
    # ✅ Tourist creates booking
    # ---------------------------
    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "tourist":
            raise PermissionDenied("Only tourists can create bookings.")

        participant_id = self.request.data.get("participant")
        participant = get_object_or_404(TourParticipant, id=participant_id)

        if participant.user != user:
            raise PermissionDenied("You can only create bookings for yourself.")

        # Auto-set booking amount from tour cost
        serializer.save(
            participant=participant,
            amount=participant.tour.cost_per_person,
            payment_status="pending",
            payment_method=self.request.data.get("payment_method", "online")
        )

    # ---------------------------
    # ✅ Tourist online partial/full payment
    # ---------------------------
    @action(detail=True, methods=["patch"], url_path="pay")
    def pay(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        if user.role != "tourist" or booking.participant.user != user:
            raise PermissionDenied()

        amount = request.data.get("amount")
        if not amount:
            return Response({"detail": "Amount required."}, status=400)

        amount = Decimal(amount)
        booking.amount_paid += amount

        if booking.amount_paid < booking.amount:
            booking.payment_status = "partial"
        else:
            # Only auto-mark paid for online payments
            if booking.payment_method != "cash":
                booking.payment_status = "paid"
                booking.paid_at = timezone.now()
            else:
                booking.payment_status = "partial"  # Wait for organizer verification

        booking.save()
        return Response(BookingSerializer(booking, context={"request": request}).data)

    # ---------------------------
    # ✅ Organizer collects cash (partial/full)
    # ---------------------------
    @action(detail=True, methods=["patch"], url_path="cash-collect")
    def cash_collect(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        if user.role != "organizer":
            raise PermissionDenied("Only organizers can collect cash.")

        if booking.participant.tour.organizer != user:
            raise PermissionDenied()

        amount = request.data.get("amount")
        if not amount:
            return Response({"detail": "Amount required."}, status=400)

        amount = Decimal(amount)
        booking.amount_paid += amount
        booking.payment_method = "cash"

        # Never auto-mark full payment for cash; always wait for verify
        if booking.amount_paid < booking.amount:
            booking.payment_status = "partial"
        else:
            booking.payment_status = "partial"  # still partial until organizer verifies

        booking.save()
        return Response(BookingSerializer(booking, context={"request": request}).data)

    # ---------------------------
    # ✅ Admin/Organizer manually verify full payment
    # ---------------------------
    @action(detail=True, methods=["patch"], url_path="verify")
    def verify_payment(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        # Permission checks
        if user.role not in ["admin", "organizer"]:
            raise PermissionDenied()

        if user.role == "organizer" and booking.participant.tour.organizer != user:
            raise PermissionDenied()

        # ✅ Only verify if actually fully paid
        if booking.amount_paid < booking.amount:
            return Response(
                {"detail": "Cannot verify partial payment. Collect full payment first."},
                status=400
            )

        if booking.payment_status == "paid":
            return Response({"detail": "Already verified."}, status=400)

        booking.payment_status = "paid"
        booking.paid_at = timezone.now()
        booking.save()

        return Response(
            BookingSerializer(booking, context={"request": request}).data
        )
