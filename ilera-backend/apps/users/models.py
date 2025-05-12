from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_farmer = models.BooleanField(default=False)
    is_vet = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="farmer_profile")
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Farmer Profile ({self.pk}): {self.user.phone}"

    class Meta:
        verbose_name = "Farmer Profile"


class VetProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="vet_profile")
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    num_ratings = models.PositiveIntegerField()
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Vet Profile ({self.pk}): {self.user.phone}"

    class Meta:
        verbose_name = "Vet Profile"
