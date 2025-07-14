from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('organizer', 'Organizer'), ('tourist', 'Tourist')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True)
    current_location = models.JSONField(null=True, blank=True)  # latitude & longitude for map integration

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # change this to avoid clash
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set_permissions",  # change this as well
        blank=True,
        help_text="Specific permissions for this user."
    )