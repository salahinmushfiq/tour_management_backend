# tours/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Guide(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='guide'
    )
    bio = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='guides/', blank=True, null=True)

    def __str__(self):
        return self.user.email


class Tour(models.Model):
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_tours',
        limit_choices_to={'role': 'organizer'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    is_custom_group = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=0)
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, default="Adventure")

    # Tourists (ManyToMany through model)
    participants = models.ManyToManyField(
        User,
        through='TourParticipant',
        related_name='joined_tours',
        limit_choices_to={'role': 'tourist'},
        blank=True
    )

    # Guides
    guides = models.ManyToManyField(
        'tours.Guide',
        related_name='tours',
        blank=True
    )

    def __str__(self):
        return self.title


class TourParticipant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='tour_participants'  # ✅ avoids clash
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tour_participations',  # ✅ avoids clash
        limit_choices_to={'role': 'tourist'}
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('tour', 'user')

    def __str__(self):
        return f"{self.user.email} in {self.tour.title}"


class TourGuideAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='guide_assignments')
    guide = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'guide'}  # Only guide users
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('tour', 'guide')  # Prevent duplicate assignments

    def __str__(self):
        return f"{self.tour.title} - {self.guide.email} ({self.status})"

class Offer(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"



class TourChatMessage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} on {self.created_at}"


class TourRating(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tour', 'user')

    def __str__(self):
        return f"{self.rating} stars by {self.user.username} for {self.tour.title}"