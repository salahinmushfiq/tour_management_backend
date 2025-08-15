# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('tourist', 'Tourist'),
        ('organizer', 'Organizer'),
        ('guide', 'Guide'),
        ('admin', 'Admin'),
    )
    LOGIN_METHOD_CHOICES = [
        ('regular', 'Regular'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tourist')  # ✅ add this
    login_method = models.CharField(max_length=10, choices=LOGIN_METHOD_CHOICES, default='regular')  # 👈
    contact_number = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_picture = models.CharField(max_length=250, blank=True, null=True)
    location = models.CharField(blank=True, max_length=255, null=True)
    bio = models.CharField(blank=True, max_length=255, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # no username required

    def __str__(self):
        return self.email
