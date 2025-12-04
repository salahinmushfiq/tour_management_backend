# bookings/management/commands/approve_and_create_bookings.py
from django.core.management.base import BaseCommand
from tours.models import TourParticipant
from bookings.models import Booking

class Command(BaseCommand):
    help = "Approve pending participants in bulk and create bookings in the new bookings app"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tour',
            type=int,
            help='Only approve participants for a specific tour ID'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of participants to approve (optional)'
        )

    def handle(self, *args, **options):
        tour_id = options.get('tour')
        limit = options.get('limit')

        qs = TourParticipant.objects.filter(status='pending')

        if tour_id:
            qs = qs.filter(tour_id=tour_id)

        if limit:
            qs = qs[:limit]

        approved_count = 0
        bookings_created = 0

        for participant in qs:
            # Approve participant
            participant.status = 'approved'
            participant.save()
            approved_count += 1

            # Create booking if not exists
            if not Booking.objects.filter(participant=participant).exists():
                Booking.objects.create(
                    participant=participant,
                    amount=participant.tour.cost_per_person,
                    amount_paid=0,
                    payment_status='pending'
                )
                bookings_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{approved_count} participants approved, {bookings_created} bookings created."
        ))
