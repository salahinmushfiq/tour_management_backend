# locations/models.py
from django.db import models
from django.conf import settings
from tours.models import Tour


class VisitedRegion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visited_regions')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='regions')
    region_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    visited_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.region_name}"


class TourLocation(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='locations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location of {self.user.username} at {self.timestamp}"

