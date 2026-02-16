# tours/management/commands/update_tour_dates.py
from django.core.management.base import BaseCommand
from tours.models import Tour
from datetime import timedelta
from django.utils.timezone import now
import random

class Command(BaseCommand):
    help = "Update all tours to have future dates"

    def handle(self, *args, **kwargs):
        tours = Tour.objects.all()
        for tour in tours:
            start_offset = random.randint(5, 60)
            tour.start_date = now().date() + timedelta(days=start_offset)
            tour.end_date = tour.start_date + timedelta(days=random.randint(3, 12))
            tour.save()
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {tours.count()} tours with future dates."))