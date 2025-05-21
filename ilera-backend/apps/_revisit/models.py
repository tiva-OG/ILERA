from django.db import models
from django.conf import settings
import uuid

from apps.users.models import FarmerProfile, VetProfile
from apps.livestock.models import Livestock

# remove _revisit from git directories


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="appointments")
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name="appointments")
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE, related_name="appointments")

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)  # optional until accepted
    notes = models.TextField(blank=True)  # notes after or during visit

    class Meta:
        ordering = ["-request_time"]

    def __str__(self):
        return f"Appointment - {self.farmer.user.phone} with {self.vet.user.phone} for {self.livestock.category} [{self.livestock.tag_id}]"
