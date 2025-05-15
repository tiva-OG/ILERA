from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class Livestock(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("unknown", "Unknown"),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="livestock")
    category = models.CharField(max_length=50)
    tag_id = models.CharField(max_length=50, unique=True)
    specie = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="unknown")
    birth_year = models.PositiveIntegerField()
    image = models.ImageField(upload_to="livestock_images/", null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        return date.today().year - self.birth_year

    def __str__(self):
        return f"{self.category} ({self.tag_id})"
