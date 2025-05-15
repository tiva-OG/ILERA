from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import uuid

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("farmer", "Farmer"),
        ("vet", "Veterinarian"),
        ("admin", "Admin"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=False)

    # removed from logic; kept for migration compatibility
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_farmer(self):
        return self.role == "farmer"

    @property
    def is_vet(self):
        return self.role == "vet"


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
    num_ratings = models.PositiveIntegerField(null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Vet Profile ({self.pk}): {self.user.phone}"

    class Meta:
        verbose_name = "Vet Profile"
