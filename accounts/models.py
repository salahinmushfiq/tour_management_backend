from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        ORGANIZER = 'organizer', _('Organizer')
        TOURIST = 'tourist', _('Tourist')

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.TOURIST
    )
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    REQUIRED_FIELDS = ['email']

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

    def __str__(self):
        return f"{self.username} ({self.role})"
