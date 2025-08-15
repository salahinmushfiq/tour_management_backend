# costs/models.py
from django.db import models
from django.conf import settings
from tours.models import Tour

class CostEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='costs')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='cost_entries')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"