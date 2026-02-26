from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")

    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    login_time = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=True)

    def __str__(self):
        status = "success" if self.was_successful else "failed"
        return f"{self.user.username} [{status}] @ {self.login_time}"

    class Meta:
        verbose_name_plural = "Login Activities"
        ordering = ["-login_time"]


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

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    class Meta:
        verbose_name_plural = "Account Statuses"


# Auto-create UserProfile and AccountStatus when a new User is created
@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        AccountStatus.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
