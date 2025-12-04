from django.core.management.base import BaseCommand
from tours.models import Booking as OldBooking
from bookings.models import Booking as NewBooking
from django.utils import timezone


class Command(BaseCommand):
    help = "Transfer bookings from tours.Booking to bookings.Booking"

    def handle(self, *args, **kwargs):
        count = 0
        for old in OldBooking.objects.all()[:10]:
            # Check if already exists to avoid duplicates
            if NewBooking.objects.filter(participant=old.participant).exists():
                continue

            new_booking = NewBooking.objects.create(
                participant=old.participant,
                amount=old.amount,
                amount_paid=old.amount_paid,
                payment_status=old.payment_status.lower(),  # match choices
                payment_method=getattr(old, 'payment_method', 'online'),
                paid_at=getattr(old, 'paid_at', None) or None,
                created_at=old.created_at or timezone.now()
            )
            new_booking.update_status()  # or update_payment_status()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} bookings transferred successfully."))
