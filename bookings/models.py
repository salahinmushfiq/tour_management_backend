# bookings/models.py
from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    participant = models.OneToOneField(
        'tours.TourParticipant',
        on_delete=models.CASCADE,
        related_name='booking'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self):
        if self.amount_paid == 0:
            self.payment_status = "pending"
        elif self.amount_paid < self.amount:
            self.payment_status = "partial"
        else:
            self.payment_status = "paid"
        self.save()
