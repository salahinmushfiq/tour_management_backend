# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    METHOD_CHOICES = [
        ("sslcommerz", "SSLCOMMERZ"),
        ("cash", "Cash"),
    ]

    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    # link payment to booking (one booking can have many payments over time)
    booking = models.ForeignKey("bookings.Booking", on_delete=models.CASCADE, related_name="payments")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True)  # who initiated (tourist or organizer)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=32, choices=METHOD_CHOICES)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="initiated")
    transaction_id = models.CharField(max_length=128, blank=True, null=True)  # gateway trx id, or organizer note
    gateway_payload = models.JSONField(null=True, blank=True)  # raw response from gateway or admin note
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="verified_payments")
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_success(self, transaction_id=None, payload=None):


        with transaction.atomic():
            if transaction_id:
                self.transaction_id = transaction_id
            if payload:
                self.gateway_payload = payload

            # idempotent: if already success, just update verified_by/time if needed
            if self.status == "success":
                if not self.verified_at:
                    self.verified_at = timezone.now()
                self.save()
                return

            self.status = "success"
            self.verified_at = timezone.now()
            self.save()

            # reflect into booking
            booking = self.booking
            booking.amount_paid = (booking.amount_paid or Decimal("0")) + Decimal(str(self.amount))

            # update booking status
            if booking.amount_paid >= booking.amount:
                booking.payment_status = "paid"
                booking.paid_at = timezone.now()
            elif booking.amount_paid > 0:
                booking.payment_status = "partial"

            booking.save()

    def mark_failed(self, payload=None):
        self.status = "failed"
        if payload:
            self.gateway_payload = payload
        self.save()

    def __str__(self):
        return f"Payment {self.id} for booking {self.booking_id} ({self.status})"
