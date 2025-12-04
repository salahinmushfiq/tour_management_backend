from django.core.management.base import BaseCommand
from tours.models import TourParticipant
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Create bookings for all approved participants without bookings'

    def handle(self, *args, **kwargs):
        approved_participants = TourParticipant.objects.filter(status='approved').exclude(booking__isnull=False)
        count = 0
        for participant in approved_participants:
            Booking.objects.create(
                participant=participant,
                amount=participant.tour.cost_per_person,
                amount_paid=0,
                payment_status='pending'
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} bookings.'))
