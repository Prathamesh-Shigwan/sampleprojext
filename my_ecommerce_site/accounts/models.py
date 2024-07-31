# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=100)
    username = models.CharField(max_length=100, unique=True)
    bio = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=200, unique=True, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    zipcode = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile_signal(sender, instance, created, **kwargs):
    create_profile(sender, instance, created, **kwargs)
