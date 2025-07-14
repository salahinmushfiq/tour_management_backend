from django.db import models
from django.conf import settings

class Guide(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='guides/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Tour(models.Model):
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'organizer'})
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    is_custom_group = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=0)
    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True)
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class Offer(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"

class TourParticipant(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'tourist'})
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tour', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.tour.title}"
