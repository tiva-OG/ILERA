import uuid
from datetime import date
from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import ULIDModel

User = get_user_model()


class Genders(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    UNKNOWN = "UNKNOWN", "Unknown"


class HealthStatus(models.TextChoices):
    HEALTHY = "HEALTHY", "Healthy"
    SICK = "SICK", "Sick"
    TREATING = "TREATING", "Treating"
    DEAD = "DEAD", "Dead"


class Livestock(ULIDModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="livestock")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="livestock", to_field="id", db_column="owner_id")
    tag_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=Genders.choices, default=Genders.UNKNOWN)
    birth_year = models.PositiveIntegerField()
    image = models.ImageField(upload_to="livestock_images/", null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    health_status = models.CharField(max_length=20, choices=HealthStatus.choices, default=HealthStatus.HEALTHY)

    @property
    def age(self):
        return date.today().year - self.birth_year

    def get_fullname(self):
        return f"{self.category} [{self.tag_id}]"

    def __str__(self):
        return f"{self.category} ({self.tag_id})"

    class Meta:
        ordering = ["tag_id", "registered_at"]
