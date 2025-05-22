import uuid
from django.db import models
from django.utils import timezone

from apps.core.models import ULIDModel
from apps.livestock.models import Livestock
from apps.users.models import FarmerProfile, VetProfile


class SessionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"
    CANCELLED = "CANCELLED", "Cancelled"
    TERMINATED = "TERMINATED", "Terminated"


class RecordType(models.TextChoices):
    SYMPTOM = "SYMPTOM", "Symptom"
    TREATMENT = "TREATMENT", "Treatment"
    VACCINATION = "VACCINATION", "Vaccination"


class CareSession(ULIDModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="sessions")
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name="sessions")
    status = models.CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["vet"]),
        ]
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session for {self.farmer.user.get_fullname()} with {self.vet.user.get_fullname()} - {self.status}"

    @property
    def is_active(self):
        return self.status == SessionStatus.ACCEPTED

    @property
    def farmer_livestock(self):
        # returns all livestock owned by farmer
        return Livestock.objects.filter(owner=self.farmer)

    def start(self):
        self.status = SessionStatus.ACCEPTED
        self.started_at = timezone.now()
        self.save()

    def terminate(self):
        self.status = SessionStatus.TERMINATED
        self.ended_at = timezone.now()
        self.save()

    def cancel(self):
        self.status = SessionStatus.CANCELLED
        self.save()

    def decline(self):
        self.status = SessionStatus.DECLINED
        self.save()


class HealthRecord(ULIDModel):
    session = models.ForeignKey(CareSession, on_delete=models.CASCADE)
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE, related_name="records")
    record_type = models.CharField(max_length=15, choices=RecordType.choices)
    notes = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.record_type} record for {self.livestock.get_fullname()}"
