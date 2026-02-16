# management/commands/create_bookings_for_approved.py
from django.core.management.base import BaseCommand
from tours.models import TourParticipant
from bookings.models import Booking

class Command(BaseCommand):
    help = "Create bookings for approved participants"

    def handle(self, *args, **kwargs):
        participants = TourParticipant.objects.filter(status="approved")
        created_count = 0
        for participant in participants:
            if not Booking.objects.filter(participant=participant).exists():
                Booking.objects.create(
                    participant=participant,
                    amount=participant.tour.cost_per_person,
                    amount_paid=0,
                    payment_status="pending"
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"{created_count} bookings created for approved participants."))