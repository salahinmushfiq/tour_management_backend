# bookings/management/commands/clear_bookings.py
from django.core.management.base import BaseCommand
from bookings.models import Booking

class Command(BaseCommand):
    help = "Delete all bookings"

    def handle(self, *args, **kwargs):
        count = Booking.objects.count()
        Booking.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} bookings."))