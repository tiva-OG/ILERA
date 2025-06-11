from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import ULIDModel


User = get_user_model()


class NotificationType(models.TextChoices):
    CARE_REQUEST_SENT = "CARE_REQUEST_SENT", "CARE_REQUEST_SENT"
    CARE_REQUEST_ACCEPTED = "CARE_REQUEST_ACCEPTED", "CARE_REQUEST_ACCEPTED"
    CARE_REQUEST_DECLINED = "CARE_REQUEST_DECLINED", "CARE_REQUEST_DECLINED"
    CARE_REQUEST_CONCLUDED = "CARE_REQUEST_CONCLUDED", "CARE_REQUEST_CONCLUDED"


class Notification(ULIDModel):
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=150)
    body = models.TextField()

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="notifications_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_received")

    metadata = models.JSONField(default=dict, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} -> {self.receiver} @ {self.created_at:strftime('%Y-%m-%d %H:%M')}"

    # id: '1',
    # title: 'Cow 150 Temperature dropped',
    # message: 'pig with tag no: 234 has dropped...',
    # time: 'now',
    # read: false,
    # icon: 'cow',
    # date: 'today',
