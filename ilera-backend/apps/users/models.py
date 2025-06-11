from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid

from .managers import UserManager
from apps.core.models import ULIDModel


class UserRole(models.TextChoices):
    FARMER = "FARMER", "Farmer"
    VET = "VET", "Vet"
    ADMIN = "ADMIN", "Admin"


class PendingUser(ULIDModel):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    password = models.CharField(max_length=128)  # hashed already
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 600


class User(AbstractBaseUser, PermissionsMixin, ULIDModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=UserRole.choices)
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
        return self.role == UserRole.FARMER

    @property
    def is_vet(self):
        return self.role == UserRole.VET

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.phone} ({self.role})"


def profile_picture_upload_path(instance, filename):
    return f"profile_pics/user_{instance.user.id}/{filename}"


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="farmer_profile")
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Farmer Profile"
        ordering = ["user__first_name", "user__last_name"]

    def save(self, *args, **kwargs):
        try:
            farmer = FarmerProfile.objects.get(pk=self.pk)
            if farmer.profile_picture and farmer.profile_picture != self.profile_picture:
                farmer.profile_picture.delete(save=False)
        except FarmerProfile.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Farmer Profile ({self.pk}): {self.user.phone}"


class VetProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="vet_profile")
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    license_number = models.CharField(unique=True, max_length=50, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Vet Profile"
        ordering = ["user__first_name", "user__last_name"]

    def save(self, *args, **kwargs):
        try:
            vet = VetProfile.objects.get(pk=self.pk)
            if vet.profile_picture and vet.profile_picture != self.profile_picture:
                vet.profile_picture.delete(save=False)
        except VetProfile.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vet Profile ({self.pk}): {self.user.phone}"
