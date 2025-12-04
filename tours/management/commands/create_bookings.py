# from django.core.management.base import BaseCommand
# from tours.models import TourParticipant, Booking
# from django.utils import timezone
# import random
#
#
# class Command(BaseCommand):
#     help = "Create bookings for all approved participants who don't have a booking yet"
#
#     def handle(self, *args, **kwargs):
#         approved_participants = TourParticipant.objects.filter(status="approved")
#         created_count = 0
#
#         for participant in approved_participants:
#             if not Booking.objects.filter(participant=participant).exists():
#                 amount = random.choice([50, 100, 150])  # Example amounts
#                 Booking.objects.createBooking.objects.create(
#                     participant=participant,
#                     amount=amount,
#                     amount_paid=0,
#                     payment_status="pending",
#                 )
#                 created_count += 1
#                 self.stdout.write(self.style.SUCCESS(
#                     f"Created booking for participant {participant.user.email} (Tour: {participant.tour.title})"
#                 ))
#
#         if created_count == 0:
#             self.stdout.write(self.style.WARNING("No new bookings created."))
#         else:
#             self.stdout.write(self.style.SUCCESS(f"Total bookings created: {created_count}"))


from django.core.management.base import BaseCommand
from tours.models import Booking

class Command(BaseCommand):
    help = "Remove bookings of participants who are not approved"

    def handle(self, *args, **kwargs):
        # Filter bookings where the participant is not approved
        invalid_bookings = Booking.objects.filter(participant__status__in=["pending", "rejected"])
        count = invalid_bookings.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No invalid bookings found."))
            return

        invalid_bookings.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} bookings for unapproved/rejected participants."))
