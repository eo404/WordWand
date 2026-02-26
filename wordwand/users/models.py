from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")

    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    login_time = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=True)


class AccountStatus(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('DEACTIVATED', 'Deactivated'),
        ('BANNED', 'Banned'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    reason = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)